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
    if (res.ok) {
      const html = await res.text();
      graphElem.innerHTML = html;
      const scripts = graphElem.getElementsByTagName('script');
      for (var i = 0; i < scripts.length; i++) {
        eval(scripts[i].innerHTML);
      }
      return true;
    }
    return false;
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
