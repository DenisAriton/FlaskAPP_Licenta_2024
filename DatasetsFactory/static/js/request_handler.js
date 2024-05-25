document.addEventListener("DOMContentLoaded", function (){
    function deleteImage(){
        fetch(delete_url,{
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "X-CSRFToken": csrf_token
            },
            "body": JSON.stringify(img_name)
        }).then(response => response.json()).then(data => {
                if (data.good === true){
                    Swal.fire({
                              icon: "success",
                              title: "Done!",
                              text: "You have deleted the profile image!",
                            }).then(response => {
                                if (response.isConfirmed === true){
                                    location.reload();
                                }else{
                                    location.reload();
                                }
                            });
                }else if (data.noimage === true){
                    Swal.fire({
                              icon: "error",
                              text: "Upload an image first!",
                            });
                }
            });
    }


    document.getElementById('delete-image').addEventListener('click', deleteImage);
    // Facem autosubmit pentru formularul de UploadImage
    document.getElementById('InputImage').addEventListener('input',function(){
        document.getElementById('FormImage').submit();
    });
});
function toogle_edit(id_group){
    const div_edit = document.getElementById(id_group);
    if (div_edit.style.display === 'none'){
        div_edit.style.display = 'block';
    }else if (div_edit.style.display === 'block'){
        div_edit.style.display = 'none';
    }
}
// Trigger de tooltip! Daca nu functioneaza aici, il vom introduce in template-uri!
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));



