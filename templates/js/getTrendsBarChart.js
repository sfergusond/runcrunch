const getTrendsBarChart = async (metric, period) => {
  try {
    const res = await fetch('{% url "getTrendsBarChart" %}', {
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
    });
    if (res.ok) {
      const html = await res.text();
      const graphElem = document.getElementById(`${period}Chart`);
      renderGraph(graphElem, html);
    }
  }
  catch (err) {
    console.log(err);
  }
}