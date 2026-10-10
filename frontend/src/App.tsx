import { useEffect, useState } from "react";
import EpaChart from "./EpaChart";
type Team = { abbr: string };

type StatRow = {
  team: string;
  season: number;
  side: string;
  plays: number;
  epa_per_play: number;
  success_rate: number;
};

const SEASONS = [2023, 2024, 2025];

export default function App() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [team, setTeam] = useState("");
  const [season, setSeason] = useState(2025);
  const [side, setSide] = useState("offense");
  const [rows, setRows] = useState<StatRow[]>([]);
  const [error, setError] = useState("");

  // Load the team list once, when the page opens
  useEffect(() => {
    fetch("/api/teams/")
      .then((r) => r.json())
      .then((data) => setTeams(data.results))
      .catch(() => setError("Could not load teams"));
  }, []);

  // Reload stats whenever a dropdown changes
  useEffect(() => {
    const params = new URLSearchParams({ season: String(season), side });
    if (team) params.set("team", team);
    fetch(`/api/team-stats/?${params}`)
      .then((r) => r.json())
      .then((data) => {
        setRows(data);
        setError("");
      })
      .catch(() => setError("Could not load stats"));
  }, [team, season, side]);

  // Offense: higher EPA is better. Defense: lower is better.
  const sorted = [...rows].sort((a, b) =>
    side === "defense"
      ? a.epa_per_play - b.epa_per_play
      : b.epa_per_play - a.epa_per_play
  );

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: "0 auto" }}>
      <h1>NFL Analytics</h1>

      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <select value={team} onChange={(e) => setTeam(e.target.value)}>
          <option value="">All teams</option>
          {teams.map((t) => (
            <option key={t.abbr} value={t.abbr}>{t.abbr}</option>
          ))}
        </select>

        <select value={season} onChange={(e) => setSeason(Number(e.target.value))}>
          {SEASONS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>

        <select value={side} onChange={(e) => setSide(e.target.value)}>
          <option value="offense">Offense</option>
          <option value="defense">Defense</option>
        </select>
      </div>

      {error && <p>{error}</p>}
      <EpaChart rows={sorted} side={side} />

      <table style={{ width: "100%", textAlign: "left" }}>
        <thead>
          <tr>
            <th>Team</th>
            <th>Season</th>
            <th>Plays</th>
            <th>EPA/play</th>
            <th>Success rate</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((r) => (
            <tr key={`${r.team}-${r.season}`}>
              <td>{r.team}</td>
              <td>{r.season}</td>
              <td>{r.plays}</td>
              <td>{r.epa_per_play.toFixed(3)}</td>
              <td>{(r.success_rate * 100).toFixed(1)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}