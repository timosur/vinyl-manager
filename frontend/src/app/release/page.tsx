import { releaseService } from "@/service/release"

export default async function Release() {
  const releases = await releaseService.get()

  return (
    <table className="table-auto">
      <thead>
        <tr>
          <th>id</th>
          <th>short</th>
          <th>name</th>
          <th>tracks</th>
          <th>labels</th>
          <th>artists</th>
        </tr>
      </thead>
      <tbody>
        {releases?.map((release: any) => (
          <tr key={release.id}>
            <td>{release.id}</td>
            <td>{release.short}</td>
            <td>{release.name}</td>
            <td>{release.tracks.map((track: any) => track.name).join(", ")}</td>
            <td>{release.labels.map((label: any) => label.name).join(", ")}</td>
            <td>{release.artists.map((artist: any) => artist.name).join(", ")}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
