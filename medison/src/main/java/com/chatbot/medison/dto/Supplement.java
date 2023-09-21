package com.chatbot.medison.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.ToString;

@Data
@ToString
@AllArgsConstructor
@NoArgsConstructor
public class Supplement {

    private int idx;    //순번

    private String name;    // 영양제이름

    private String brand;   // 영양제 제조사

    private String price;   // 가격

    private String image;   // 이미지

    private String nutrient_info;   // 영양성분 정보

    private String info;        // 상품 정보

    private String use_info;    // 상품 사용법

    private String caution;     // 상품 주의사항

    private String category;    // 상품 분류

    private String rating_count;    // 리뷰수

    private String link; // 링크
}
