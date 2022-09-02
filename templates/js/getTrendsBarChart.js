async function getTrendsBarChart(metric, period) {
  fetch('{% url "getTrendsBarChart" %}', {
    method: 'POST',
    headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': '{{ csrf_token }}'
    },
    body: JSON.stringify({
      'athlete': {{ request.athlete.id }},
      'metric': metric,
      'period': period
    })
  })
  .then((response) => {
    return response.text();
  })
  .then((html) => {
    const graphElem = document.getElementById(`${period}Chart`);
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