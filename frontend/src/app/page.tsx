// Dashboard of the vinyl manager, explains what it does
export default async function Page() {

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-xl font-bold mb-4">Vinyl Collection</h1>
      <div className="mb-4">
        <p>This is a tool to manage your vinyl collection.</p>
        <p>It can import CSV files from <a href="https://www.deejay.de/">Deejay.de</a> and sync with <a href="https://www.discogs.com/">Discogs</a>.</p>
      </div>
      <div>
        <p>It is a work in progress, so don&rsquo;t expect too much.</p>
      </div>
    </div>
  )
}
