fetch('{% url "getHeatmap" %}', {
  method: 'POST',
  headers: {
  'Content-Type': 'application/json',
  'X-CSRFToken': '{{ csrf_token }}'
  },
  body: JSON.stringify({
    'athlete': {{ request.athlete.id }}
  })
})
.then((response) => {
  return response.text();
})
.then((html) => {
  const graphElem = document.getElementById('heatmap');
  graphElem.innerHTML = html;
  const scripts = graphElem.getElementsByTagName('script')
  for (var i = 0; i < scripts.length; i++) {
    eval(scripts[i].innerHTML);
  }
})
.catch((error) => {
  console.log(error);
});
