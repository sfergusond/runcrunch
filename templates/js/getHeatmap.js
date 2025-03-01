const getHeatmap = async (graphElem) => {
  try {
    const res = await fetch('{% url "getHeatmap" %}', {
      method: 'POST',
      headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': '{{ csrf_token }}'
      },
      body: JSON.stringify({
        'athlete': {{ request.athlete.id }}
      })
    });
    if (!res.ok) {
      return false
    }

    var html = "";
    for await (const chunk of res.body.values()) {
        html += String.fromCharCode.apply(null, chunk)
    }

    renderGraph(graphElem, html);
    return true;
  }
  catch (err) {
    console.log(err);
    return false;
  }
}

const graphElem = document.getElementById('heatmap');
graphElem.innerHTML = '<h3 class="text-center">Loading...</h3>';
(async () => {
  let success = await getHeatmap(graphElem);
  while (!success) {
    graphElem.innerHTML = '<h3 class="text-center">Loading...</h3>';
    success = getHeatmap(graphElem);
  }
})();
