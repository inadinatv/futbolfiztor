import combined from "../../data/combined.json";

export const dynamic = "force-static";

const DISPLAY_TIMEZONE = "Europe/Istanbul";

const STATUS_TR = {
  NS: "Başlamadı",
  "1H": "İlk Yarı",
  HT: "Devre Arası",
  "2H": "İkinci Yarı",
  ET: "Uzatmalar",
  P: "Penaltı",
  FT: "Bitti",
  AET: "Uzatma Sonu",
  PEN: "Penaltı Sonu",
  PST: "Ertelendi",
  CANC: "İptal",
  ABD: "Yarım Kaldı",
  AWD: "Hükmen",
  WO: "Hükmen",
  LIVE: "Canlı",
};

function formatGenerated(value) {
  if (!value) return "-";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "-";

  return new Intl.DateTimeFormat("tr-TR", {
    timeZone: DISPLAY_TIMEZONE,
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function formatMatchTime(timestamp) {
  if (!timestamp) return "-";

  const date = new Date(timestamp * 1000);

  if (Number.isNaN(date.getTime())) return "-";

  return new Intl.DateTimeFormat("tr-TR", {
    timeZone: DISPLAY_TIMEZONE,
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function scoreText(match) {
  if (match?.goals?.home == null || match?.goals?.away == null) {
    return "-";
  }

  return `${match.goals.home} - ${match.goals.away}`;
}

function statusText(match) {
  return STATUS_TR[match?.short] || match?.status || "-";
}

function oddsText(match) {
  const bookmakers = match?.odds?.bookmakers;
  const first = Array.isArray(bookmakers) ? bookmakers[0] : null;
  const odds = Array.isArray(first?.odds) ? first.odds : [];

  if (!odds.length) return "-";

  return odds
    .slice(0, 3)
    .map((o) => `${o?.label ?? "?"}: ${o?.value ?? "?"}`)
    .join(" | ");
}

const styles = {
  container: {
    maxWidth: 1200,
    margin: "0 auto",
    padding: "24px 16px",
  },
  header: {
    marginBottom: 24,
  },
  h1: {
    margin: "0 0 8px",
    fontSize: 30,
  },
  h2: {
    margin: "0 0 14px",
    fontSize: 22,
  },
  meta: {
    margin: "4px 0",
    color: "#94a3b8",
  },
  notice: {
    background: "#7c2d12",
    border: "1px solid #fdba74",
    padding: "10px 12px",
    borderRadius: 10,
  },
  card: {
    background: "#111827",
    border: "1px solid #1f2937",
    borderRadius: 14,
    padding: 16,
    marginBottom: 16,
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    minWidth: 760,
  },
  th: {
    textAlign: "left",
    padding: "8px 6px",
    borderBottom: "1px solid #334155",
    color: "#94a3b8",
    fontSize: 12,
  },
  td: {
    padding: "8px 6px",
    borderBottom: "1px solid #1e293b",
    fontSize: 14,
  },
  center: {
    textAlign: "center",
  },
  right: {
    textAlign: "right",
  },
  footer: {
    marginTop: 28,
    color: "#94a3b8",
    fontSize: 12,
  },
};

export default function HomePage() {
  const fixtures = Array.isArray(combined?.fixtures) ? combined.fixtures : [];
  const standings = Array.isArray(combined?.standings)
    ? combined.standings
    : [];

  const leagueMap = new Map();

  for (const fixture of fixtures) {
    const key = fixture?.league?.id ?? "other";

    if (!leagueMap.has(key)) {
      leagueMap.set(key, {
        league: fixture?.league ?? null,
        matches: [],
      });
    }

    leagueMap.get(key).matches.push(fixture);
  }

  const leagues = Array.from(leagueMap.values()).sort((a, b) =>
    (a.league?.name || "").localeCompare(b.league?.name || "", "tr")
  );

  return (
    <main style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.h1}>Günün Maçları ve Puan Durumu</h1>
        <p style={styles.meta}>
          Maç tarihi: {combined?.matchesDate ?? "-"}
        </p>
        <p style={styles.meta}>
          Son güncelleme: {formatGenerated(combined?.generatedAt)}
        </p>

        {combined?.notice ? (
          <p style={styles.notice}>{combined.notice}</p>
        ) : null}
      </header>

      <section>
        <h2 style={styles.h2}>Günün Maçları</h2>

        {leagues.length === 0 ? (
          <p>
            Henüz maç verisi yok. GitHub Actions workflow çalıştırıldığında
            veri gelecek.
          </p>
        ) : null}

        {leagues.map(({ league, matches }) => {
          const sorted = [...matches].sort(
            (a, b) => (a?.timestamp || 0) - (b?.timestamp || 0)
          );

          return (
            <article key={league?.id ?? "other"} style={styles.card}>
              <h3 style={{ margin: "0 0 10px", fontSize: 18 }}>
                {league?.name ?? "Diğer"}
                {league?.country ? ` • ${league.country}` : ""}
              </h3>

              <div style={{ overflowX: "auto" }}>
                <table style={styles.table}>
                  <thead>
                    <tr>
                      <th style={styles.th}>Saat</th>
                      <th style={styles.th}>Ev Sahibi</th>
                      <th style={{ ...styles.th, ...styles.center }}>
                        Skor
                      </th>
                      <th style={styles.th}>Deplasman</th>
                      <th style={styles.th}>Durum</th>
                      <th style={styles.th}>Oran/Ücret</th>
                    </tr>
                  </thead>

                  <tbody>
                    {sorted.map((match) => (
                      <tr
                        key={
                          match?.id ??
                          `${match?.teams?.home?.id}-${match?.teams?.away?.id}`
                        }
                      >
                        <td style={styles.td}>
                          {formatMatchTime(match?.timestamp)}
                        </td>
                        <td style={styles.td}>
                          {match?.teams?.home?.name ?? "-"}
                        </td>
                        <td
                          style={{
                            ...styles.td,
                            ...styles.center,
                            fontWeight: 600,
                          }}
                        >
                          {scoreText(match)}
                        </td>
                        <td style={styles.td}>
                          {match?.teams?.away?.name ?? "-"}
                        </td>
                        <td style={styles.td}>{statusText(match)}</td>
                        <td style={styles.td}>{oddsText(match)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </article>
          );
        })}
      </section>

      <section style={{ marginTop: 28 }}>
        <h2 style={styles.h2}>Puan Durumu</h2>

        {standings.length === 0 ? (
          <p>Henüz puan durumu verisi yok.</p>
        ) : null}

        {standings.map((standing) => {
          const rows = Array.isArray(standing?.table) ? standing.table : [];

          return (
            <article
              key={`${standing?.leagueId}-${standing?.season}`}
              style={styles.card}
            >
              <h3 style={{ margin: "0 0 10px", fontSize: 18 }}>
                {standing?.name ?? "Lig"}
                {standing?.season ? ` • ${standing.season}` : ""}
              </h3>

              <div style={{ overflowX: "auto" }}>
                <table style={styles.table}>
                  <thead>
                    <tr>
                      <th style={styles.th}>#</th>
                      <th style={styles.th}>Takım</th>
                      <th style={{ ...styles.th, ...styles.center }}>O</th>
                      <th style={{ ...styles.th, ...styles.center }}>G</th>
                      <th style={{ ...styles.th, ...styles.center }}>B</th>
                      <th style={{ ...styles.th, ...styles.center }}>M</th>
                      <th style={{ ...styles.th, ...styles.center }}>AG</th>
                      <th style={{ ...styles.th, ...styles.center }}>YG</th>
                      <th style={{ ...styles.th, ...styles.center }}>AV</th>
                      <th style={{ ...styles.th, ...styles.right }}>P</th>
                    </tr>
                  </thead>

                  <tbody>
                    {rows.map((row) => (
                      <tr key={row?.teamId ?? row?.rank ?? row?.team}>
                        <td style={styles.td}>{row?.rank ?? "-"}</td>
                        <td style={styles.td}>{row?.team ?? "-"}</td>
                        <td style={{ ...styles.td, ...styles.center }}>
                          {row?.played ?? "-"}
                        </td>
                        <td style={{ ...styles.td, ...styles.center }}>
                          {row?.win ?? "-"}
                        </td>
                        <td style={{ ...styles.td, ...styles.center }}>
                          {row?.draw ?? "-"}
                        </td>
                        <td style={{ ...styles.td, ...styles.center }}>
                          {row?.lose ?? "-"}
                        </td>
                        <td style={{ ...styles.td, ...styles.center }}>
                          {row?.goalsFor ?? "-"}
                        </td>
                        <td style={{ ...styles.td, ...styles.center }}>
                          {row?.goalsAgainst ?? "-"}
                        </td>
                        <td style={{ ...styles.td, ...styles.center }}>
                          {row?.goalDiff ?? "-"}
                        </td>
                        <td
                          style={{
                            ...styles.td,
                            ...styles.right,
                            fontWeight: 700,
                          }}
                        >
                          {row?.points ?? "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </article>
          );
        })}
      </section>

      <footer style={styles.footer}>
        <p>
          Bu proje örnek bir veri botudur. Telifli analiz metinleri kazınmaz
          ve yayınlanmaz. Oran/ücret verileri yalnızca lisanslı API izni varsa
          gösterilmelidir.
        </p>
      </footer>
    </main>
  );
}
