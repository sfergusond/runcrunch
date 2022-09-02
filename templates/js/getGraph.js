async function getGraph(graphName) {
  fetch(`/graph/${graphName}`, {
    method: 'POST',
    headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': '{{ csrf_token }}'
    },
    body: activityJson
  })
  .then((response) => {
    return response.text();
  })
  .then((html) => {
    const graphElem = document.getElementById(graphName);
    graphElem.innerHTML = html;
    const scripts = graphElem.getElementsByTagName('script')
    for (var i = 0; i < scripts.length; i++) {
      eval(scripts[i].innerHTML);
    }
  })
  .catch((error) => {
    console.log(error);
  });
}
