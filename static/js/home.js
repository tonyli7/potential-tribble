function countdown(yr,m,d,h,min){
    var today=new Date()
    console.log(today.toString());
    var to = new Date(yr,m-1,d,h,min,0,0)
    console.log(to.toString());
    var diff = to-today;
    var daydiff = Math.floor(diff/1000/60/60/24);
    diff -= 1000*60*60*24*daydiff;
    var hrdiff = Math.floor(diff/1000/60/60);
    diff -= 1000*60*60*hrdiff;
    var mindiff = Math.floor(diff/1000/60);
    diff -= 1000*60*mindiff;
    var secdiff = Math.floor(diff/1000);
    document.getElementById("clock").innerHTML = daydiff + " days " + hrdiff + " hours " + mindiff + " minutes " + secdiff + " seconds"
    setTimeout(function(){countdown(yr,m,d,h,min)},100);
}

el = document.getElementById("clock");
countdown(el.getAttribute("data-year"),el.getAttribute("data-month"),el.getAttribute("data-day"),el.getAttribute("data-hour"),el.getAttribute("data-minute"));
