export default function MetricTile({ label, value, detail }) {
  return (
    <section className="metric-tile">
      <span>{label}</span>
      <strong>{value}</strong>
      {detail && <small>{detail}</small>}
    </section>
  );
}
