var login_view = document.getElementById("login_display");
var register_view = document.getElementById("register_display");
var belay_view = document.getElementById("belay_display");
// var  = document.getElementById("join_chat_display");
var session_token;
var channelname = "";
var messageid;          // message for current replies
var username = "";

function login() {


    var getReq = new XMLHttpRequest();
    getReq.open("POST", "/api/login");
    getReq.addEventListener("load", login_message);
    // oReq.setRequestHeader("Ocp-Apim-Subscription-Key","a5d9d1bfbba4442d98e393b08e2e9c2f");
   
    var email = document.getElementById("login_email").value;
    var password = document.getElementById("login_password").value;
    console.log(email);
    console.log(password);
    
    getReq.setRequestHeader("email",email);
    getReq.setRequestHeader("password",password);
   
    getReq.send();
}

function login_message() {
    var text = JSON.parse(this.responseText);
    console.log(text);

    if(text["login_code"] == "true") {
        console.log("login success");
        window.session_token = text["session_token"];
        window.username = text["username"];
        belay_display();
    }
    else {
        document.getElementById("login_error").innerText = "email or password not correct, please try again";
    }

}

function register() {
   // iregister

    console.log("register");
    register_display();
   
    var getReq = new XMLHttpRequest();
    getReq.open("POST", "/api/register");
    getReq.addEventListener("load", register_message);
    // oReq.setRequestHeader("Ocp-Apim-Subscription-Key","a5d9d1bfbba4442d98e393b08e2e9c2f");

    var username = document.getElementById("register_username").value;
    var password = document.getElementById("register_password").value;
    var email =  document.getElementById("register_email").value;

    getReq.setRequestHeader("username",username);
    getReq.setRequestHeader("password",password);
    getReq.setRequestHeader("email",email);
   
    getReq.send();

}



function register_message() {
    var text = JSON.parse(this.responseText);
    console.log(text);

    if(text["register_code"] == "true") {
        console.log("register success");
        login_display();
    }
    else {
        document.getElementById("register_error").innerText = "This email has been registered, please use another email or login";
    }
}

function forget_password() {
    var getReq = new XMLHttpRequest();
    getReq.open("POST", "/api/forget_password");
    getReq.addEventListener("load", forget_password_message);
    // oReq.setRequestHeader("Ocp-Apim-Subscription-Key","a5d9d1bfbba4442d98e393b08e2e9c2f");

    var email =  document.getElementById("login_email").value;

    getReq.setRequestHeader("email",email); 
    getReq.send();
}

function forget_password_message() {
    var text = JSON.parse(this.responseText);
    console.log(text);

    if(text["forget_password_code"] == "true") {
        console.log("magic link is sent to your email");
        document.getElementById("login_error").innerText = "A magic link is sent to your email";
    }
    else {
        document.getElementById("login_error").innerText = "This email has no account in belay, please do registraion";
    }
}

function create_channel() {
    var channelname = document.getElementById("create_channel").value;
    if(channelname.length != 0) {
        var getReq = new XMLHttpRequest();
        getReq.open("POST", "/api/create_channel");
        // getReq.addEventListener("load", forget_password_message);
        message = JSON.stringify({"session_token":window.session_token,"channelname":channelname});
        console.log(message);
        getReq.send(message);
    }
}

function delete_channel() {

}



function send_message() {
    var content = document.getElementById("message_content").value;
    if(content.length != 0) {
        var getReq = new XMLHttpRequest();
        getReq.open("POST", "/api/send_message");
        message = JSON.stringify({"session_token":window.session_token,"channelname":window.channelname,"content":content});
        console.log(message);
        getReq.send(message); 

        request_messages_in_channel();
    }
}

function select_channel(channelname) {
    console.log(channelname);
    messages_display();
    thread_hide();
    window.channelname = channelname;
    request_messages_in_channel();
}

function request_messages_in_channel() {
    var getReq = new XMLHttpRequest();
    getReq.open("POST", "/api/request_messages_in_channel");
    message = JSON.stringify({"session_token":window.session_token,"channelname":window.channelname});
    getReq.addEventListener("load", get_messages_in_channel);
    console.log(message);
    getReq.send(message); 
}

function get_messages_in_channel() {
    console.log(this.responseText);
    var text = JSON.parse(this.responseText);
    var str = "";
    
    text["messages"].forEach(function(message) {
        var messageid = message[0];
        var username = message[1];
        var content = message[2];
        var reply_number = message[3];
        
        var substr = '<label>' + username  + ':</label>' + '<div>' + content + '</div>';
        if(reply_number === 0) {
             substr = substr + '<button onclick="select_reply(\'' + messageid  + '\')"> Reply </button>'
        }
        else {
             substr = substr + '<button onclick="select_reply(\'' + messageid + '\')"> show ' + reply_number + ' replies</button>'
        }
       
        substr = substr + '<br></br>';
        // '<button onclick="select_channel(\'' + channelname +'\');">' + channelname + '  ' + unread_count + '</button><br></br>';
        str = str + substr;
    });
    console.log(str);

    document.getElementById("messages").innerHTML = str;

}

function select_reply(messageid) {
    console.log(messageid);
    window.messageid = messageid;
    thread_display();
    request_replies_in_message();

}

function send_reply() {
    var content = document.getElementById("reply_content").value;
    if(content.length != 0) {
        var getReq = new XMLHttpRequest();
        getReq.open("POST", "/api/send_reply");
        message = JSON.stringify({"session_token":window.session_token,"messageid":window.messageid,"content":content});
        console.log(message);
        getReq.send(message); 

        request_replies_in_message();
    }
}

function request_replies_in_message() {
    var getReq = new XMLHttpRequest();
    getReq.open("POST", "/api/request_replies_in_message");
    message = JSON.stringify({"session_token":window.session_token,"messageid":window.messageid});
    getReq.addEventListener("load", get_replies_in_message);
    console.log(message);
    getReq.send(message); 
}

function get_replies_in_message() {
    console.log(this.responseText);
    var text = JSON.parse(this.responseText);
    var str = "";
    
    text["replies"].forEach(function(reply) {
        var username = reply[0];
        var content = reply[1];
        
        var substr = '<label>' + username  + ':</label>' + '<div>' + content + '</div>';
        substr = substr + '<br></br>';
        str = str + substr;
    });
    console.log(str);
    document.getElementById("replies").innerHTML = str;
}


function request_data() {     
    var getReq = new XMLHttpRequest();
    getReq.open("POST", "/api/request_data");
    getReq.addEventListener("load", process_data);

    var dic = {"session_token":window.session_token}
    if(window.channelname != "") {
        dic["channelname"] = window.channelname;
    }

    message = JSON.stringify(dic);
    console.log(message);
    getReq.send(message); 
}

function process_data() {
    console.log(this.responseText);
    var text = JSON.parse(this.responseText);
    var str = "";
    text["channels"].forEach(function(channel) {
        var channelname = channel[0];
        var unread_count = channel[1];
        console.log(channel);
        var substr = '<button onclick="select_channel(\'' + channelname +'\');">' + channelname + '</button><label>  ' + unread_count + ' unread messages</label><br></br>';
        str = str + substr;
    });

    console.log(str);
    document.getElementById("channels").innerHTML = str;
}



function login_display() {
    login_view.style.display = 'block';
    register_view.style.display = 'none';
    belay_view.style.display = 'none';
    // history.pushState({},"","/chat/"+chat_id);
   
    /*
       */
}

function channel_message() {
    console.log(this.responseText);
    var text = JSON.parse(this.responseText);
    
}

function register_display() {
    login_view.style.display = 'none';
    register_view.style.display = 'block';
    // history.pushState({},"","/chat/"+chat_id);
    belay_view.style.display = 'none';
    console.log("register_dispaly()");
}

function belay_display() {
    login_view.style.display = 'none';
    register_view.style.display = 'none';
    belay_view.style.display = 'block';
    // history.pushState({},"","/chat/"+chat_id);
    
    document.getElementById("username_display").innerHTML = window.username;
    setInterval(request_data,500);
    request_data();
}

function thread_hide() {
    document.getElementById("right").style.display = 'none';
    document.getElementById("belay_display").style.columnCount = 2;
}

function thread_display() {
    document.getElementById("right").style.display = 'block';
    document.getElementById("belay_display").style.columnCount = 3;
}

function messages_display() {
    document.getElementById("mid").style.display = 'block';
}

login_display();


