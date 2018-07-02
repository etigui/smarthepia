
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
        span.text("Not running");
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