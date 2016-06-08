function countdown(yr,m,d,h,min){
    console.log("HI")
    var today=new Date()
    var to = new Date(yr,m,d,h,min,0,0)
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
countdown(el.getAttribute("data-a"),el.getAttribute("data-b"),el.getAttribute("data-c"),el.getAttribute("data-d"),el.getAttribute("data-e"));
