fetch('{% url "dashboardTable" %}', {
  method: 'POST',
  headers: {
  'Content-Type': 'application/json',
  'X-CSRFToken': '{{ csrf_token }}'
  },
  body: JSON.stringify({
    'athlete': {{ request.athlete.id }},
    'fromDate': '{{ fromDate|date:"Y-m-d" }}',
    'toDate': '{{ toDate|date:"Y-m-d" }}'
  })
})
.then((response) => {
  return response.text();
})
.then((html) => {
  const graphElem = document.getElementById('dashboardTable');
  graphElem.innerHTML += html;
  $('#dashboardTable').DataTable({
    paging: true,
    searching: true,
    ordering:  true,
    order: [],
    columnDefs: [
      { type: 'any-number', targets : [2, 5] },
      { type: 'time-uni', targets : 3 }
    ]
  });
  $('#activities_wrapper .dataTables_filter').find('label').find('input').addClass('form-control form-control-sm');
  $('#activities_wrapper .dataTables_filter').find('label').addClass('form-check-inline');
  $('#activities_wrapper .dataTables_length').find('label').find('select').addClass('form-control-flush');
  $('#activities_wrapper .dataTables_paginate').find('span').each(function() {
    const $this = $(this);
    this.removeClass("current page-link");
    this.removeClass("paginate_button");
    this.addClass("page-link")
  });
  $('#activities_wrapper .dataTables_paginate').addClass("pagination");
} );

_anyNumberSort = function(a, b, high) {
  var reg = /[+-]?((\d+(\.\d*)?)|\.\d+)([eE][+-]?[0-9]+)?/;       
  a = a.replace(',','.').match(reg);
  a = a !== null ? parseFloat(a[0]) : high;
  b = b.replace(',','.').match(reg);
  b = b !== null ? parseFloat(b[0]) : high;
  return ((a < b) ? -1 : ((a > b) ? 1 : 0));   
}
  
jQuery.extend( jQuery.fn.dataTableExt.oSort, {
  "any-number-asc": function (a, b) {
    return _anyNumberSort(a, b, Number.POSITIVE_INFINITY);
  },
  "any-number-desc": function (a, b) {
    return _anyNumberSort(a, b, Number.NEGATIVE_INFINITY) * -1;
  },
  "time-uni-pre": function (a) {
    var uniTime;
  
    if (a.toLowerCase().indexOf("am") > -1 || (a.toLowerCase().indexOf("pm") > -1 && Number(a.split(":")[0]) === 12)) {
      uniTime = a.toLowerCase().split("pm")[0].split("am")[0];
      while (uniTime.indexOf(":") > -1) {
        uniTime = uniTime.replace(":", "");
      }
    } else if (a.toLowerCase().indexOf("pm") > -1 || (a.toLowerCase().indexOf("am") > -1 && Number(a.split(":")[0]) === 12)) {
      uniTime = Number(a.split(":")[0]) + 12;
      var leftTime = a.toLowerCase().split("pm")[0].split("am")[0].split(":");
      for (var i = 1; i < leftTime.length; i++) {
        uniTime = uniTime + leftTime[i].trim().toString();
      }
    } else {
      uniTime = a.replace(":", "");
      while (uniTime.indexOf(":") > -1) {
        uniTime = uniTime.replace(":", "");
      }
    }
    return Number(uniTime);
  },
  
  "time-uni-asc": function (a, b) {
    return ((a < b) ? -1 : ((a > b) ? 1 : 0));
  },
  
  "time-uni-desc": function (a, b) {
    return ((a < b) ? 1 : ((a > b) ? -1 : 0));
  }
});
