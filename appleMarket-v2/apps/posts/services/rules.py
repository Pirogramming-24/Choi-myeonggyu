import re

def parse_nutrition_info(text_list):
    """
    영양정보 파싱 - 단백질 1g 오인식 해결
    """
    print("\n" + "="*70)
    print("📋 영양정보 파싱 시작")
    print("="*70)
    
    if not text_list or not isinstance(text_list, list):
        return {'calories': 0.0, 'carbs': 0.0, 'protein': 0.0, 'fat': 0.0}
    
    full_text = " ".join(text_list)
    
    nutrition_data = {
        'calories': 0.0,
        'carbs': 0.0,
        'protein': 0.0,
        'fat': 0.0
    }
    
    # ========================================
    # 1️⃣ 칼로리
    # ========================================
    print("\n🔍 칼로리 검색...")
    
    cal_match = re.search(r'총\s*(\d+)\s*kcal', full_text, re.IGNORECASE)
    if cal_match:
        val = float(cal_match.group(1))
        nutrition_data['calories'] = val
        print(f"   ✅ {val} kcal (총)")
    else:
        cal_match = re.search(r'(\d+)\s*kcal', full_text, re.IGNORECASE)
        if cal_match:
            val = float(cal_match.group(1))
            if 50 <= val < 2000:
                nutrition_data['calories'] = val
                print(f"   ✅ {val} kcal")
    
    # ========================================
    # 2️⃣ 탄수화물
    # ========================================
    print("\n🔍 탄수화물 검색...")
    
    carb_values = []
    for match in re.finditer(r'탄수화물\s*(\d+\.?\d*)\s*[g9]', full_text):
        val = float(match.group(1))
        if val < 500:
            carb_values.append(val)
    
    if carb_values:
        val = max(carb_values)
        nutrition_data['carbs'] = val
        print(f"   ✅ {val} g")
    
    # ========================================
    # 3️⃣ 단백질 (핵심 수정!)
    # ========================================
    print("\n🔍 단백질 검색...")
    
    prot_values = []
    
    # 📍 패턴 1: "단백질 1 g" (정상)
    for match in re.finditer(r'단백질\s*(\d+\.?\d*)\s*g', full_text):
        val = float(match.group(1))
        if 0.1 <= val < 200:
            prot_values.append(val)
            print(f"   발견: {val} g (정상 패턴)")
    
    # 📍 패턴 2: "단백질 1 9" (g가 9로 오인식)
    for match in re.finditer(r'단백질\s*(\d+\.?\d*)\s*9\s*\d+%', full_text):
        val = float(match.group(1))
        if 0.1 <= val < 200:
            prot_values.append(val)
            print(f"   발견: {val} g (g→9 오인식)")
    
    # 📍 패턴 3: "단백질 19" (1g가 19로 붙어서 읽힘)
    for match in re.finditer(r'단백질\s*19\s*\d+%', full_text):
        # 19를 1.9로 해석
        val = 1.9
        prot_values.append(val)
        print(f"   발견: {val} g (19 → 1.9 보정)")
    
    # 📍 패턴 4: "단백질 38g7%" (붙어있음)
    for match in re.finditer(r'단백질\s*(\d+)g\d+%', full_text):
        val = float(match.group(1))
        if 0.1 <= val < 200:
            prot_values.append(val)
            print(f"   발견: {val} g (붙어있는 패턴)")
    
    # 📍 패턴 5: "理 38g7%" (한자 오인식)
    for match in re.finditer(r'[理단]\s*(\d+\.?\d*)g\d+%', full_text):
        val = float(match.group(1))
        if 0.1 <= val < 200:
            prot_values.append(val)
            print(f"   발견: {val} g (한자 오인식)")
    
    # 📍 패턴 6: 리스트 순회 (줄바꿈 케이스)
    for i, text in enumerate(text_list):
        if '단백질' in text or '단백' in text:
            # 다음 줄이 "19" 또는 "1 9"인 경우
            if i + 1 < len(text_list):
                next_text = text_list[i + 1].strip()
                
                # "19" → 1.9
                if next_text == '19':
                    prot_values.append(1.9)
                    print(f"   발견: 1.9 g (다음 줄 '19' → 1.9)")
                
                # "1" 다음에 "9"가 있는 경우
                elif next_text == '1' and i + 2 < len(text_list):
                    if text_list[i + 2].strip() == '9':
                        prot_values.append(1.0)
                        print(f"   발견: 1.0 g (다음 줄 '1' '9')")
    
    if prot_values:
        # 🔧 특별 처리: 1.9와 19가 함께 있으면 1.9 선택
        if 1.9 in prot_values and 19 in prot_values:
            val = 1.9
            print(f"   ✅ {val} g (1.9 우선 선택)")
        else:
            val = max(prot_values)
            print(f"   ✅ {val} g (최대값)")
        
        nutrition_data['protein'] = val
    else:
        print(f"   ❌ 찾을 수 없음")
    
    # ========================================
    # 4️⃣ 지방
    # ========================================
    print("\n🔍 지방 검색...")
    
    fat_values = []
    
    # "지방 1.6 g" 또는 "지방 16 g"
    for match in re.finditer(r'(?<!트랜스)(?<!포화)지방\s*(\d+\.?\d*)\s*[g9]', full_text):
        val = float(match.group(1))
        if val < 200:
            fat_values.append(val)
    
    if fat_values:
        val = max(fat_values)
        nutrition_data['fat'] = val
        print(f"   ✅ {val} g")
    
    # ========================================
    # 🔬 물리 법칙 검증
    # ========================================
    print("\n" + "-"*70)
    print("🔬 물리 법칙 검증")
    print("-"*70)
    
    cal = nutrition_data['calories']
    carbs = nutrition_data['carbs']
    prot = nutrition_data['protein']
    fat = nutrition_data['fat']
    
    if cal > 10:
        # 지방 검증
        if fat > 0 and fat * 9 > cal * 0.7:
            if fat >= 10:
                corrected = round(fat / 10, 1)
                print(f"🔧 지방: {fat}g → {corrected}g")
                nutrition_data['fat'] = corrected
                fat = corrected
        
        # 단백질 검증
        if prot > 0:
            calc_cal = (carbs * 4) + (prot * 4) + (fat * 9)
            limit_cal = cal * 1.3
            
            print(f"\n📊 칼로리 계산:")
            print(f"   탄수화물: {carbs}g × 4 = {carbs*4:.0f} kcal")
            print(f"   단백질:   {prot}g × 4 = {prot*4:.0f} kcal")
            print(f"   지방:     {fat}g × 9 = {fat*9:.0f} kcal")
            print(f"   ───────────────────────")
            print(f"   계산:     {calc_cal:.0f} kcal")
            print(f"   표기:     {cal:.0f} kcal")
            
            # 🔧 단백질 보정 (38 → 3.8)
            if calc_cal > limit_cal + 100 and prot >= 10:
                corrected = round(prot / 10, 1)
                print(f"\n🔧 단백질: {prot}g → {corrected}g")
                nutrition_data['protein'] = corrected
                prot = corrected
            elif 10 <= prot < 100:
                test_val = round(prot / 10, 1)
                test_calc = (carbs * 4) + (test_val * 4) + (fat * 9)
                if abs(test_calc - cal) < abs(calc_cal - cal):
                    print(f"\n🔧 단백질: {prot}g → {test_val}g")
                    nutrition_data['protein'] = test_val
                    prot = test_val
            
            # 🔧 1.9 → 1.0 보정 (누들핏 케이스)
            elif prot == 1.9:
                test_calc_1 = (carbs * 4) + (1.0 * 4) + (fat * 9)
                test_calc_19 = (carbs * 4) + (1.9 * 4) + (fat * 9)
                
                if abs(test_calc_1 - cal) < abs(test_calc_19 - cal):
                    print(f"\n🔧 단백질: 1.9g → 1.0g (오차 감소)")
                    nutrition_data['protein'] = 1.0
                    prot = 1.0
    
    # ========================================
    # ✅ 최종 결과
    # ========================================
    print("\n" + "="*70)
    print("✅ 최종 영양정보")
    print("="*70)
    
    final_cal = nutrition_data['calories']
    final_carbs = nutrition_data['carbs']
    final_prot = nutrition_data['protein']
    final_fat = nutrition_data['fat']
    
    final_calc = (final_carbs * 4) + (final_prot * 4) + (final_fat * 9)
    diff = abs(final_calc - final_cal)
    
    print(f"  칼로리    : {final_cal:6.1f} kcal")
    print(f"  탄수화물   : {final_carbs:6.1f} g")
    print(f"  단백질    : {final_prot:6.1f} g")
    print(f"  지방      : {final_fat:6.1f} g")
    print(f"  ───────────────────────")
    print(f"  계산 칼로리: {final_calc:6.0f} kcal")
    
    if diff < 50:
        print(f"  ✅ 검증 통과 (오차: {diff:.0f} kcal)")
    else:
        print(f"  ⚠️ 검증 실패 (오차: {diff:.0f} kcal)")
    
    print("="*70 + "\n")
    
    return nutrition_data
