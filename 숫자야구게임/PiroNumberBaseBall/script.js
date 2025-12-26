// 1. 전역 변수 설정
let answer_numbers = [];
let attempts = 9;

// 2. 게임 초기화 및 정답 생성 함수
function initGame() {
    attempts = 9;
    answer_numbers = [];
    
    // 0~9 사이의 중복되지 않는 랜덤 숫자 3개 생성
    let numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
    for (let i = 0; i < 3; i++) {
        const index = Math.floor(Math.random() * numbers.length);
        answer_numbers.push(numbers[index]);
        numbers.splice(index, 1); 
    }

    console.log("정답:", answer_numbers);

    // 화면 초기화
    document.getElementById('attempts').innerText = attempts;
    document.getElementById('results').innerHTML = '';
    
    // 이미지 초기화 (파일 위치가 script.js와 같다면 './success.png')
    document.getElementById('game-result-img').src = ''; 
    
    clearInputs();
    
    const btn = document.querySelector('.submit-button');
    if (btn) btn.disabled = false;
}

function clearInputs() {
    const input1 = document.getElementById('number1');
    const input2 = document.getElementById('number2');
    const input3 = document.getElementById('number3');
    
    input1.value = '';
    input2.value = '';
    input3.value = '';
    input1.focus();
}

// 3. 숫자 확인 함수
function check_numbers() {
    const input1 = document.getElementById('number1');
    const input2 = document.getElementById('number2');
    const input3 = document.getElementById('number3');

    const val1 = input1.value;
    const val2 = input2.value;
    const val3 = input3.value;

    // 예외 처리
    if (val1 === '' || val2 === '' || val3 === '') {
        clearInputs();
        return;
    }

    if (isNaN(val1) || isNaN(val2) || isNaN(val3)) {
        clearInputs();
        return;
    }

    const user_numbers = [parseInt(val1), parseInt(val2), parseInt(val3)];
    
    // 스트라이크, 볼 판정
    let strike = 0;
    let ball = 0;

    for (let i = 0; i < 3; i++) {
        if (user_numbers[i] === answer_numbers[i]) {
            strike++;
        } else if (answer_numbers.includes(user_numbers[i])) {
            ball++;
        }
    }

    // --- 결과 화면 출력 (HTML 생성) ---
    const resultDiv = document.getElementById('results');
    const checkResultDiv = document.createElement('div');
    checkResultDiv.className = 'check-result';

    // 1. 왼쪽: 입력한 숫자
    const leftDiv = document.createElement('div');
    leftDiv.className = 'left';
    leftDiv.innerText = `${val1} ${val2} ${val3}`;
    checkResultDiv.appendChild(leftDiv);

    // ✨ 2. 중간: 콜론(:) 추가 (이 부분이 추가되었습니다!) ✨
    const colonDiv = document.createElement('div');
    colonDiv.innerText = ':';
    colonDiv.style.margin = '0 10px'; // 좌우 간격 살짝 띄우기
    colonDiv.style.fontWeight = 'bold'; // 글씨 굵게
    colonDiv.style.color = '#555';      // 너무 진하지 않은 회색
    checkResultDiv.appendChild(colonDiv);

    // 3. 오른쪽: 결과(S/B/O)
    const rightDiv = document.createElement('div');
    rightDiv.className = 'right';

    if (strike === 0 && ball === 0) {
        const outSpan = document.createElement('span');
        outSpan.className = 'num-result out';
        outSpan.innerText = 'O';
        rightDiv.appendChild(outSpan);
    } else {
        if (strike > 0) {
            const strikeSpan = document.createElement('span');
            strikeSpan.className = 'num-result strike';
            strikeSpan.innerText = strike + 'S';
            rightDiv.appendChild(strikeSpan);
            
            // S와 B 사이 간격용 공백
            rightDiv.appendChild(document.createTextNode(' '));
        }
        if (ball > 0) {
            const ballSpan = document.createElement('span');
            ballSpan.className = 'num-result ball';
            ballSpan.innerText = ball + 'B';
            rightDiv.appendChild(ballSpan);
        }
    }
    
    checkResultDiv.appendChild(rightDiv);
    resultDiv.appendChild(checkResultDiv);

    // --- 게임 종료 로직 ---
    
    // 승리
    if (strike === 3) {
        // 이미지가 같은 폴더에 있다고 가정
        document.getElementById('game-result-img').src = './success.png';
        endGame();
        return;
    }

    // 횟수 차감
    attempts--;
    document.getElementById('attempts').innerText = attempts;

    // 패배
    if (attempts <= 0) {
        document.getElementById('game-result-img').src = './fail.png';
        endGame();
        return;
    }

    clearInputs();
}

function endGame() {
    const btn = document.querySelector('.submit-button');
    if (btn) btn.disabled = true;
}

window.onload = initGame;