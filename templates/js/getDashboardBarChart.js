fetch('{% url "dashboardBarChart" %}', {
  method: 'POST',
  headers: {
  'Content-Type': 'application/json',
  'X-CSRFToken': '{{ csrf_token }}'
  },
  body: JSON.stringify({
    'athlete': {{ request.athlete.id }},
    'fromDate': '{{ fromDate|date:"Y-m-d" }}',
    'toDate': '{{ toDate|date:"Y-m-d" }}',
    'metric': '{{ metric }}'
  })
})
.then((response) => {
  return response.text();
})
.then((html) => {
  const graphElem = document.getElementById('{{ metric }}Chart');
  graphElem.innerHTML = html;
  const scripts = graphElem.getElementsByTagName('script')
  for (var i = 0; i < scripts.length; i++) {
    eval(scripts[i].innerHTML);
  }
})
.catch((error) => {
  console.log(error);
});
