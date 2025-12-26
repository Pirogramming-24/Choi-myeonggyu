window.onload=function(){
    
    const pw_show_hide = document.querySelector('.pw_show_hide')
    const input_id = document.querySelector('input[type=text]')
    const input_pw = document.querySelector('input[type=password]')
    const id_error = document.querySelector('.id_error')
    const pw_error = document.querySelector('.pw_error')
    console.log(pw_show_hide, input_id, input_pw, id_error, pw_error)

    input_id.addEventListener('click', function(){
        id_error.style.display = 'block';
    });

    input_pw.addEventListener('click', function(){
        pw_error.style.display = 'block'; 
    });

    let i = true
    pw_show_hide.addEventListener('click', function(){
        if(i == true){ // 눈을 떴을 때 (보여야 함)
            pw_show_hide.style.backgroundPosition = '-126px 0'
            i = false
            // [핵심 기능 추가] 비밀번호 창을 일반 텍스트 창으로 변경
            input_pw.type = 'text'; 
        } else { // 눈을 감았을 때 (숨겨야 함)
            i = true
            pw_show_hide.style.backgroundPosition = '-105px 0'
            // [핵심 기능 추가] 다시 비밀번호 창으로 변경
            input_pw.type = 'password'; 
        }
    })

} //onload end