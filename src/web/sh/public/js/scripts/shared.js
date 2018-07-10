
//The ticking clock function
function timeTick(){
    //grab updated time
    timeLocal = new Date();
    //add time difference
    timeLocal.setMilliseconds(timeLocal.getMilliseconds() - millDiff);
    //display the value

    document.getElementById("serverTime").innerHTML = formatDate(timeLocal);
}

// Update the badge on the navbar
// If atype == -1 or count == -1 => no alarm not ack
function updateBadge(span, atype, count){

    // Set number of alarm not ack
    if(count === -1){
        span.text("");
    }else{
        span.text(count);
    }

    // Remove last class => color
    // Then we can add the new class
    if(span.hasClass('badge-danger')){
        span.removeClass("badge-danger");
    }else if(span.hasClass('badge-warning')){
        span.removeClass("badge-warning");
    }else{
        span.removeClass("badge-info");
    }

    if(atype !== -1) {

        // Add badge class => color
        if (atype === 1) {
            span.addClass("badge-danger");
        } else if (atype === 2) {
            span.addClass("badge-warning");
        } else {
            span.addClass("badge-info");
        }
    }
}

// Format date for user like => DD:MM:YYYY HH:MM:SS
function formatDate(timeLocal){
    var hour = timeLocal.getHours();
    var min = timeLocal.getMinutes();
    var sec = timeLocal.getSeconds();
    var day = timeLocal.getDate();
    var month = (timeLocal.getMonth() + 1);
    var year = timeLocal.getFullYear();
    hour = hour < 10 ? '0'+ hour : hour;
    min= min < 10 ? '0'+ min : min;
    sec = sec < 10 ? '0'+ sec : sec;
    day = day < 10 ? '0'+ day : day;
    month = month < 10 ? '0'+ month : month;
    return day + "." + month + "." + year +" " + hour + ":" + min + ":" + sec;
}

function timeStatus(){

    // Get last update time and remove string before
    // Compare with datetime now
    var lastUpdateTime = $('#lastUpdateStatus').text().replace('Last update ','');
    var now = new Date();
    var subMinutes = now.setMinutes(now.getMinutes() - 6);
    var lastDate = new Date(lastUpdateTime);

    if (subMinutes > lastDate) {

        var knx = $('#knxrestStatus');
        var automation = $('#automationStatus');

        // Remove last class => color
        // Then we can add the new class
        if(knx.hasClass('bg-danger')){
            knx.removeClass("bg-danger");
        }else if(knx.hasClass('bg-warning')){
            knx.removeClass("bg-warning");
        }else{
            knx.removeClass("bg-success");
        }
        if(automation.hasClass('bg-danger')){
            automation.removeClass("bg-danger");
        }else if(automation.hasClass('bg-warning')){
            automation.removeClass("bg-warning");
        }else{
            automation.removeClass("bg-success");
        }

        // Add default knx => not running
        // Add status message
        knx.addClass("bg-danger");
        knx.text("Not up-to-date");

        // Add default automation => not running
        // Add status message
        automation.addClass("bg-danger");
        automation.text("Not up-to-date");
    }
}

// Update knx and automation datas status
function updateStatus(item, span, updateTime){

    // Remove last class => color
    // Then we can add the new class
    if(span.hasClass('bg-danger')){
        span.removeClass("bg-danger");
    }else if(span.hasClass('bg-warning')){
        span.removeClass("bg-warning");
    }else{
        span.removeClass("bg-success");
    }

    // Get current datetime and compare with last status
    // If last status is older then 6 min => error
    var now = new Date();
    var subMinutes = now.setMinutes(now.getMinutes() - 6);
    var lastDate = new Date(item['updatetime']);
    if (subMinutes > lastDate){

        // Add default => not running
        span.addClass("bg-danger");

        // Add status message
        span.text("Not up-to-date");
        updateTime.text("Last update " + item['updatetime']);
    }else{

        // Add class => color
        if (item.color === 1) {
            span.addClass("bg-success");
        } else if (item.color === 2) {
            span.addClass("bg-warning");
        } else {
            span.addClass("bg-danger");
        }

        // Add status message
        span.text(item['status']);
        updateTime.text("Last update " + item['updatetime']);
    }
}

// Process knx and automation datas status
function updateAllStatus(automation, knx, lastUpdate, data){
    $.each(data, function (i, item) {
        if(item['name'] === "knx"){
            updateStatus(item, knx, lastUpdate);
        }else if(item['name'] === "automation"){
            updateStatus(item, automation, lastUpdate);
        }
    });
}

// Month here is 1-indexed (January is 1, February is 2, etc). This is
// because we're using 0 as the day so that it returns the last day
// of the last month, so you have to add 1 to the month number
// so it returns the correct amount of days
function daysInMonth (month) {
    var today = new Date();
    return new Date(today.getFullYear(), month, 0).getDate();
}

// Add day by month in select
function addDaysInSelect(month, select){

    select.removeAttr('disabled');
    select.empty().append('<option value="" selected disabled hidden>Select day</option>');

    nbOfDay = daysInMonth(month);
    var step;
    for (step = 1; step <= nbOfDay; step++) {
        select.append($('<option>', {
            value: step,
            text : step
        }));
    }
}

// Check if number is float
function isFloat(n) {
    return n === +n && n !== (n|0);
}

// Check if number is integer
function isInteger(n) {
    return n === +n && n === (n|0);
}

// Check if the number is a float
function parsToFloat(number){
    f = parseFloat(number);
    return !isNaN(f);

}

// Check if the number is a float
function parsToInt(number){
    i = parseInt(number);
    return !isNaN(i);

}
