import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import "dotenv/config";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, "..", "data");

const BASE_URL =
  process.env.FOOTBALL_API_BASE_URL || "https://v3.football.api-sports.io";

const API_KEY = process.env.FOOTBALL_API_KEY || "";

const LEAGUE_IDS = (process.env.LEAGUE_IDS || "203")
  .split(",")
  .map((x) => x.trim())
  .filter(Boolean);

const SEASON = process.env.SEASON || String(new Date().getFullYear());
const TIMEZONE = process.env.TIMEZONE || "Europe/Istanbul";
const FETCH_ODDS = process.env.FETCH_ODDS === "true";
const MAX_ODDS_FIXTURES =
  Number(process.env.MAX_ODDS_FIXTURES || 10) || 10;
const REQUEST_DELAY_MS =
  Number(process.env.REQUEST_DELAY_MS || 1200) || 1200;

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function todayInTimezone() {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: TIMEZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
}

async function ensureDataDir() {
  await fs.mkdir(DATA_DIR, { recursive: true });
}

async function writeJson(fileName, data) {
  const filePath = path.join(DATA_DIR, fileName);
  await fs.writeFile(filePath, JSON.stringify(data, null, 2), "utf8");
}

async function apiGet(pathname, params = {}) {
  if (!API_KEY) {
    throw new Error("FOOTBALL_API_KEY tanımlı değil.");
  }

  const url = new URL(pathname, BASE_URL);

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });

  for (let attempt = 1; attempt <= 4; attempt += 1) {
    try {
      const res = await fetch(url, {
        headers: {
          "x-apisports-key": API_KEY,
          Accept: "application/json",
        },
      });

      if (res.status === 429 || res.status >= 500) {
        const retryAfter = Number(res.headers.get("retry-after")) || 20;
        await sleep(Math.max(retryAfter, attempt * 10) * 1000);
        continue;
      }

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`API HTTP ${res.status}: ${text.slice(0, 300)}`);
      }

      const body = await res.json();

      const errors = body?.errors;
      const hasError = Array.isArray(errors)
        ? errors.length > 0
        : Boolean(errors && Object.keys(errors).length > 0);

      if (hasError) {
        const message = Array.isArray(errors)
          ? errors.map((e) => e?.message || JSON.stringify(e)).join("; ")
          : typeof errors === "string"
            ? errors
            : JSON.stringify(errors);

        if (
          message.toLowerCase().includes("rate") ||
          message.toLowerCase().includes("limit")
        ) {
          await sleep(30_000);
          continue;
        }

        throw new Error(`API error: ${message}`);
      }

      return body;
    } catch (error) {
      if (attempt === 4) throw error;
      await sleep(5000 * attempt);
    }
  }

  throw new Error("API isteği denemelere rağmen başarısız oldu.");
}

function normalizeFixture(item) {
  return {
    id: item?.fixture?.id ?? null,
    date: item?.fixture?.date ?? null,
    timestamp: item?.fixture?.timestamp ?? null,
    status: item?.fixture?.status?.long ?? null,
    short: item?.fixture?.status?.short ?? null,
    minute: item?.fixture?.status?.elapsed ?? null,
    venue: item?.fixture?.venue?.name ?? null,
    league: {
      id: item?.league?.id ?? null,
      name: item?.league?.name ?? null,
      country: item?.league?.country ?? null,
      season: item?.league?.season ?? null,
      logo: item?.league?.logo ?? null,
    },
    teams: {
      home: {
        id: item?.teams?.home?.id ?? null,
        name: item?.teams?.home?.name ?? null,
        logo: item?.teams?.home?.logo ?? null,
        winner: item?.teams?.home?.winner ?? null,
      },
      away: {
        id: item?.teams?.away?.id ?? null,
        name: item?.teams?.away?.name ?? null,
        logo: item?.teams?.away?.logo ?? null,
        winner: item?.teams?.away?.winner ?? null,
      },
    },
    goals: {
      home: item?.goals?.home ?? null,
      away: item?.goals?.away ?? null,
    },
    odds: null,
  };
}

function normalizeStandings(body) {
  const league = body?.response?.[0]?.league;

  if (!league) return null;

  const rawStandings = Array.isArray(league.standings)
    ? league.standings.flat()
    : [];

  return {
    leagueId: league.id ?? null,
    name: league.name ?? null,
    country: league.country ?? null,
    season: league.season ?? null,
    generatedAt: new Date().toISOString(),
    table: rawStandings.map((row) => ({
      rank: row?.rank ?? null,
      teamId: row?.team?.id ?? null,
      team: row?.team?.name ?? null,
      logo: row?.team?.logo ?? null,
      points: row?.points ?? null,
      played: row?.all?.played ?? null,
      win: row?.all?.win ?? null,
      draw: row?.all?.draw ?? null,
      lose: row?.all?.lose ?? null,
      goalsFor: row?.all?.goals?.for ?? null,
      goalsAgainst: row?.all?.goals?.against ?? null,
      goalDiff: row?.goalsDiff ?? null,
      form: row?.form ?? null,
      description: row?.description ?? null,
    })),
  };
}

async function fetchOddsForFixture(fixtureId) {
  try {
    const body = await apiGet("/odds", {
      fixture: fixtureId,
    });

    const bookmakers = body?.response?.[0]?.bookmakers || [];

    if (!bookmakers.length) return null;

    return {
      source: "API-Football odds",
      bookmakers: bookmakers.slice(0, 3).map((b) => ({
        name: b?.bookmaker?.name ?? null,
        odds: (b?.odds || []).slice(0, 8).map((o) => ({
          label: o?.label ?? null,
          value: o?.value ?? null,
        })),
      })),
    };
  } catch {
    return null;
  }
}

async function fetchFixtures(date) {
  const results = [];

  for (const leagueId of LEAGUE_IDS) {
    try {
      const body = await apiGet("/fixtures", {
        date,
        league: leagueId,
        timezone: TIMEZONE,
      });

      const items = Array.isArray(body?.response) ? body.response : [];
      results.push(...items.map(normalizeFixture));
    } catch (error) {
      console.error(`Fixture hatası [league=${leagueId}]:`, error.message);
    }

    await sleep(REQUEST_DELAY_MS);
  }

  return results;
}

async function fetchStandings() {
  const results = [];

  const seasonNumber = Number(SEASON);
  const seasons = [SEASON];

  if (Number.isFinite(seasonNumber)) {
    seasons.push(String(seasonNumber - 1));
  }

  const uniqueSeasons = [...new Set(seasons)];

  for (const leagueId of LEAGUE_IDS) {
    let found = false;

    for (const season of uniqueSeasons) {
      try {
        const body = await apiGet("/standings", {
          league: leagueId,
          season,
        });

        const normalized = normalizeStandings(body);

        if (normalized?.table?.length) {
          results.push(normalized);
          found = true;
          break;
        }
      } catch (error) {
        console.error(
          `Standings hatası [league=${leagueId}, season=${season}]:`,
          error.message
        );
      }

      await sleep(REQUEST_DELAY_MS);
    }

    if (!found) {
      console.warn(
        `Standings bulunamadı: league=${leagueId}, seasons=${uniqueSeasons.join("/")}`
      );
    }
  }

  return results;
}

async function main() {
  await ensureDataDir();

  if (!API_KEY) {
    console.warn(
      "FOOTBALL_API_KEY tanımlı değil. Veri çekilmedi. Mevcut data/combined.json korunuyor."
    );
    return;
  }

  const matchesDate = todayInTimezone();
  const generatedAt = new Date().toISOString();

  const fixtures = await fetchFixtures(matchesDate);
  const standings = await fetchStandings();

  if (FETCH_ODDS) {
    const nowSeconds = Math.floor(Date.now() / 1000);

    const upcoming = fixtures
      .filter((m) => m.timestamp && m.timestamp >= nowSeconds)
      .slice(0, MAX_ODDS_FIXTURES);

    for (const match of upcoming) {
      match.odds = await fetchOddsForFixture(match.id);
      await sleep(REQUEST_DELAY_MS);
    }
  }

  const combined = {
    generatedAt,
    matchesDate,
    source: BASE_URL,
    leagueIds: LEAGUE_IDS,
    season: SEASON,
    timezone: TIMEZONE,
    notice: "",
    fixtures,
    standings,
  };

  await writeJson("combined.json", combined);

  console.log(
    `OK: ${fixtures.length} maç, ${standings.length} puan tablosu kaydedildi.`
  );
}

main().catch((error) => {
  console.error("Veri çekme başarısız:", error);
  process.exit(1);
});
