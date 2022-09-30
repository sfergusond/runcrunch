async function getGraph(graphName) {
  try {
    const res = await fetch(`/graph/${graphName}`, {
      method: 'POST',
      headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': '{{ csrf_token }}'
      },
      body: activityJson
    });
    if (res.ok) {
      const html = await res.text();
      const graphElem = document.getElementById(graphName);
      renderGraph(graphElem, html);
    }
  }
  catch (err) {
    console.log(err);
  }
}
