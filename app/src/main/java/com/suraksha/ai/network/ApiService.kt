package com.suraksha.ai.network

import okhttp3.MultipartBody
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
        @Part audio: MultipartBody.Part
    ): AnalyzeResponse

    @POST("guardian-alert")
    suspend fun guardianAlert(
        @Body request: GuardianAlertRequest
    ): GuardianAlertResponse
}