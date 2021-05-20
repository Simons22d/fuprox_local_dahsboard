let loc = window.location.hostname

const get_videos = () =>{
    $.ajax({
    url: `http://${loc}:9000/video/get/all`,
    method: "POST",
    data: {
    },
    beforeSend: ()=>{
    },
    success: function (result) {
        let handle = $("#videos");
        let final = "";
        if (result){
            result.map((video,index)=>{
                let button =  Number(video.active) ? `<div class="col-lg-2 col-sm-2 btn btn-sm btn-warning" onclick="videoStatus(this)" id="${video.id}">Deactivate</div>` : `<div class="col-lg-2 col-sm-2 btn btn-sm btn-outline-secondary" onclick="videoStatus(this)" id="${video.id}">Activate</div>` ;
                final +=`      
             <div class="col-lg-12">
               <div class="row mt-2">
                    <div class="col-lg-1 col-sm-1">${video.id}</div>
                    <div class="col-lg-7 col-sm-9">${video.name}</div>
                    ${button}
                    <div class="ml-4 col-lg-1 col-sm-2 btn btn-sm  btn-danger" id="${video.id}"onclick="delete_video(this)">Delete</div>
                </div>
            </div>
                `;
            })
            handle.html(final);
        }else{
            handle.html("<h5 class='text-muted'>No Videos Uploaded Yet</h5>")
        }
    },
    complete : ()=>{
    }
    });
}

get_videos();

// const getData = (url,methods,data,handle) => {
// 	fetch(url,{
// 	  method: methods,
// 	  headers: {
// 	    'Accept': 'application/json',
// 	    'Content-Type': 'application/json'
// 	  },
// 	  body: JSON.stringify(data)
// 	})
// 	.then(res=>res.json())
// 	.then(res => handle(res));
// };

const videoStatus = (me) => {
    console.log("id<>>>",me.id)
    getData(`http://${loc}:9000/video/toggle`,"POST",{"id":me.id},(data)=>{
        get_videos();
    })
}



const delete_video = (me) => {
    console.log(me.id)
    getData(`http://${loc}:9000/video/delete`,"POST",{"id" : me.id},(data)=>{
        get_videos()
    })
}


let current_category;

const uploadLink = () => {
    console.log(">>",sessionStorage.getItem("vid_type"),$("#link").val())
    if (sessionStorage.getItem("vid_type") && $("#link").val().length){
        getData(`http://${loc}:9000/video/link`,"POST",{
               type : sessionStorage.getItem("vid_type"),
               link : $("#link").val()
            },(data)=>{
                _("status").innerHTML = data.msg
                get_videos()
        })
    }
    console.log("upload File .....", "current_id",sessionStorage.vid_type)
}

const getType = (me) =>{
    let value = me.value
    sessionStorage.setItem("vid_type",value)
}

const changeView = (e)=> {
    let state = $('#customSwitch1').prop('checked')
    let html ;
    console.log(state)
    if(!state){
        html = `
            <h5 class="text-muted mt-2"> Upload Video</h5>
            <form id="upload_form" enctype="multipart/form-data" method="post">
                <progress id="progressBar" value="0" max="100" style="width:300px;"></progress>
                <div class="row col-lg-12 mt-4">
                  <input type="file" name="file1" id="file1"><br>
                </div>
        
                <div class="row col-lg-12 mt-3">
                      <input type="button" value="Upload File" onclick="uploadFile()"
                         class="col-lg-2 col-sm-5  custom-file-upload btn btn-sm btn-primary">
                </div>
                <style>
                      /* input[type="file"] {
                          display: none;
                      } */
                    .custom-file-upload {
                      display: inline-block;
                      padding: 6px 12px;
                      cursor: pointer;
                      color:#FFF;
                  }
                </style>
            </form>
        `
    }else{
        html = `
            <h5 class="text-muted mt-2">Add Video Stream</h5>

            <form id="upload_form_streams"  method="post">
                <div class="row col-lg-12 mt-4">
                  <input type="text" class="form-control form-control-sm col-lg-5" name="link" id="link"><br>
                </div>
                <div class="row col-lg-12 mt-3" id="">
                   <div class='form-group'>
                      <label for='Type'>Type</label>
                      <select class='form-control form-control-sm' name='category' id='vid_type' onchange="getType(this)">
                        <option value='Null'>Select Type</option>
                        <option value='2'>Youtube Link </option>
                        <option value='3'>Video Stream Link</option>
                      </select>
                    </div>
                </div>
                <div class="row col-lg-12 mt-5">
                      <input type="button" value="Upload Link" onclick="uploadLink()"
                             class="col-lg-2 col-sm-5  custom-file-upload btn btn-sm btn-primary">
                </div>
            </form>
        `
    }
    $("#uplaod_form").html(html)
}
function _(el){
	return document.getElementById(el);
}

function uploadFile(){
	var file = _("file1").files[0];
	var formdata = new FormData();
	formdata.append("file", file);
	var ajax = new XMLHttpRequest();
	ajax.upload.addEventListener("progress", progressHandler, false);
	ajax.addEventListener("load", completeHandler, false);
	ajax.addEventListener("error", errorHandler, false);
	ajax.addEventListener("abort", abortHandler, false);
	ajax.open("POST", `http://${loc}:9000/video/upload`);
	ajax.send(formdata);
}

function progressHandler(event){
	// _("loaded_n_total").innerHTML = "Uploaded "+event.loaded+" bytes of "+event.total;
	var percent = (event.loaded / event.total) * 100;
	_("progressBar").value = Math.round(percent);
	_("status").innerHTML = Math.round(percent)+"% uploaded... please wait";
}
function completeHandler(event){
	_("status").innerHTML = event.target.responseText;
	_("progressBar").value = 0;
	get_videos()
}
function errorHandler(event){
	_("status").innerHTML = "Upload Failed";
}
function abortHandler(event){
	_("status").innerHTML = "Upload Aborted";
}

let video_handle = _("videos")


$("#file").change(function() {
	vidUrl(this);
});



var icon_data;

const upload_icon_ = (e)=>{
	let icon = icon_data;
	let icon_name = $("#icon_name").val();
	if (icon && icon_name){
		getData(`http://${loc}:9000/service/icon`,"POST",{"icon" : icon, "name" : icon_name},(data)=>{
			// updateIcons()

			// updateServices()
			console.log("!!!!!!!!!!!!",data)

			if(data.status === 201){
			    // window.loc.href = (`http://${loc}:9000/icons`)
				$("#message_icon").html(`<div class="alert alert-success" role="alert">${data.msg}</div>`)
                window.location.href = `http://${loc}:9000/icons`
			}else{
				$("#message_icon").html(`<div class="alert alert-danger" role="alert">${data.msg}</div>`)
			}
		})
	}else{
		$("#message_icon").html(`<div class="alert alert-danger" role="alert">Error All Fields Data Required.</div>`)
	}
}

var video_data;
function vidUrl(input) {
	if (input.files && input.files[0]) {
		var reader = new FileReader();
		reader.onload = function(e) {
			video_data = reader.result
		}
		reader.readAsDataURL(input.files[0]); // convert to base64 string
		}
}

$("#icon_file_icon").change(function() {
	readURL(this);
});



var video_data;
function vidUrl(input) {
	if (input.files && input.files[0]) {
		var reader = new FileReader();
		reader.onload = function(e) {
			video_data = reader.result
		}
		reader.readAsDataURL(input.files[0]); // convert to base64 string
	}
}



$("#file").change(function() {
	vidUrl(this);
});




function readURL(input) {
if (input.files && input.files[0]) {
	var reader = new FileReader();
	reader.onload = function(e) {
		icon_data = reader.result
	}
	reader.readAsDataURL(input.files[0]); // convert to base64 string
	}
}

const phrase_ = () => {
    let options =  $("#options_").val();
    let phrase  = $("#new_phrase").val();
    console.log(phrase);
    console.log(options);
    getData(`http://${loc}:9000/phrase`,"POST",{"phrase" : phrase,"options" : options},(data)=>{
        console.log(data)
        window.location.href = `http://${loc}:9000/extras`
    })
}

