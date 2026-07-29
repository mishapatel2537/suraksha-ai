package com.suraksha.ai.network

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.Body
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface ApiService {

    @POST("analyze-message")
    suspend fun analyzeMessage(
        @Body request: AnalyzeRequest
    ): AnalyzeResponse

    @Multipart
    @POST("analyze-call")
    suspend fun analyzeCall(
        @Part audio: MultipartBody.Part,
        @Part("output_language") output_language: RequestBody?
    ): AnalyzeResponse

    @POST("guardian-alert")
    suspend fun guardianAlert(
        @Body request: GuardianAlertRequest
    ): GuardianAlertResponse
}