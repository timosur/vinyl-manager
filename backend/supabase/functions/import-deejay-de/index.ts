// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

Deno.serve(async (req) => {
  // Create a new Supabase client
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_ANON_KEY') ?? '',
    { global: { headers: { Authorization: req.headers.get('Authorization')! } } }
  )

  // Get the session or user object
  // const { data } = await supabase.auth.getUser()
  // const user = data.user

  try {
    // Read csv from request body
    const reqBodyRaw = await req.blob();
    const csv = await reqBodyRaw.text();

    const csvRows = csv.split('\n');
    const csvHeaders = csvRows[0].split(';');
    const csvData = csvRows.slice(1).map(row => row.split(';'));

    // convert to JSON
    const json = csvData.map(row => {
        const obj: any = {}
        csvHeaders.forEach((header, i) => {
          obj[header.replace(" ", "_").toLowerCase()] = row[i]
        })
        return obj
      }
    )

    for (const item of json.slice(1, 2)) {
      console.log(item)
        
      // insert artist
      const foundArtist = (await supabase
        .from('artist')
        .select('name')
        .eq('name', item["artist"])).data.length > 0

      if (!foundArtist) {
        const { artist, artistError } = await supabase
          .from('artist')
          .insert([
            { name: item["artist"] },
          ])
          .select()

        console.log(artist, artistError)

        if (artistError) {
          throw artistError
        }
      }

      const artistId = (await supabase
        .from('artist')
        .select('id')
        .eq('name', item["artist"])).data[0].id
      
      console.log(artistId)

      // insert label
      const foundLabel = (await supabase
        .from('label')
        .select('name')
        .eq('name', item["label"])).data?.length > 0

      if (!foundLabel) {
        const { label, labelError } = await supabase
          .from('label')
          .insert([
            { name: item["label"] },
          ])
          .select()

        console.log(label, labelError)

        if (labelError) {
          throw labelError
        }
      }

      const labelId = (await supabase
        .from('label')
        .select('id')
        .eq('name', item["label"])).data[0].id

      console.log(labelId)

      // insert record
      const foundRecord = (await supabase
        .from('record')
        .select('name')
        .eq('title', item["title"])).data?.length > 0

      if (!foundRecord) {
        const { record, recordError } = await supabase
          .from('record')
          .insert([
            { 
              title: item["title"],
            },
          ])
          .select()

        console.log(record, recordError)

        if (recordError) {
          throw recordError
        }
      }

      const recordId = (await supabase
        .from('record')
        .select('id')
        .eq('name', item["title"])).data[0].id

      console.log(recordId)

      // insert release
      const foundRelease = (await supabase
        .from('release')
        .select('name')
        .eq('name', item["label_no"])).data?.length > 0

      if (!foundRelease) {
        const { release, releaseError } = await supabase
          .from('release')
          .insert([
            { 
              name: item["label_no"],
              label_id: labelId,
              record_id: recordId,
              artist_id: artistId,
            },
          ])
          .select()

        console.log(release, releaseError)

        if (releaseError) {
          throw releaseError
        }
      }

      const releaseId = (await supabase
        .from('release')
        .select('id')
        .eq('name', item["label_no"])).data[0].id

      console.log(releaseId)
    }

    return new Response(JSON.stringify({ "hello": "Hello" }), {
      headers: { 'Content-Type': 'application/json' },
      status: 200,
    })
  } catch (err) {
    console.error(err)
    return new Response(String(err?.message ?? err), { status: 500 })
  }
})

/* To invoke locally:

  1. Run `supabase start` (see: https://supabase.com/docs/reference/cli/supabase-start)
  2. Make an HTTP request:

  curl -i --location --request POST 'http://127.0.0.1:54321/functions/v1/import-deejay-de' \
    --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0' \
    --header 'Content-Type: application/json' \
    --data '{"name":"Functions"}'

*/
