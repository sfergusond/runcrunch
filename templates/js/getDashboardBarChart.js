async function getDashboardBarChart(metric) {
  try {
    let url;
    if (metric === 'schedule') {
      url = '{% url "dashboardScheduleChart" %}';
    }
    else {
      url = '{% url "dashboardBarChart" %}';
    }
    const res = await fetch(url, {
      method: 'POST',
      headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': '{{ csrf_token }}'
      },
      body: JSON.stringify({
        'athlete': {{ request.athlete.id }},
        'fromDate': '{{ fromDate|date:"Y-m-d" }}',
        'toDate': '{{ toDate|date:"Y-m-d" }}',
        'metric': metric
      })
    });
    if (res.ok) {
      const html = await res.text();
      const graphElem = document.getElementById(`${metric}Chart`);
      renderGraph(graphElem, html);
    }
  }
  catch (err) {
    console.log(err);
  }
}