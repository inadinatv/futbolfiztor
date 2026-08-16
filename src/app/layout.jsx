export const metadata = {
  title: "Günün Maçları ve Puan Durumu",
  description:
    "GitHub Actions ile güncellenen, Vercel üzerinde yayınlanan maç ve puan durumu botu.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="tr">
      <body
        style={{
          margin: 0,
          fontFamily: "system-ui, -apple-system, sans-serif",
          background: "#0f172a",
          color: "#e2e8f0",
        }}
      >
        {children}
      </body>
    </html>
  );
}
