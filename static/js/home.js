console.log("HI");
function countdown(yr,m,d,h,min,sec){
    theyear=yr;themonth=m;theday=d
    var today=new Date()
    var todayy=y-today.getYear()
    var todaym=m-today.getMonth()
    var todayd=d-today.getDate()
    var todayh=h-today.getHours()
    var todaymin=min-today.getMinutes()
    var todaysec=sec-today.getSeconds()

    console.log(todayy+""+todaym+""+todayd)
    setTimeout(countdown(yr,m,d,h,min,sec),1000)
}

//enter the count down date using the format year/month/day
countdown(2018,12,25)
