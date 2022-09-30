const renderGraph = (graphElem, html) => {
  graphElem.innerHTML = html;
  const scripts = graphElem.getElementsByTagName('script');
  for (var i = 0; i < scripts.length; i++) {
    eval(scripts[i].innerHTML);
  }
}