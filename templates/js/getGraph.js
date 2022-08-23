fetch('{% url graphName %}', {
  method: 'POST',
  headers: {
  'Content-Type': 'application/json',
  'X-CSRFToken': '{{ csrf_token }}'
  },
  body: JSON.stringify({{ activityJson | safe }})
})
.then((response) => {
  return response.text();
})
.then((html) => {
  const graphElem = document.getElementById('{{ graphName }}');
  graphElem.innerHTML = html;
  const scripts = graphElem.getElementsByTagName('script')
  for (var i = 0; i < scripts.length; i++) {
    eval(scripts[i].innerHTML);
  }
})
.catch((error) => {
  console.log(error);
});
