package com.suraksha.ai.screens.messagecheck

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.suraksha.ai.network.RetrofitClient
import com.suraksha.ai.network.AnalyzeRequest
import com.suraksha.ai.network.AnalyzeResponse
import kotlinx.coroutines.launch

class MessageInputViewModel : ViewModel() {
    var messageText by mutableStateOf("")
        private set

    var result by mutableStateOf<AnalyzeResponse?>(null)
        private set

    var isLoading by mutableStateOf(false)
        private set

    var errorMessage by mutableStateOf<String?>(null)
        private set

    var hasLoggedResult by mutableStateOf(false)
        private set

    fun markResultLogged() {
        hasLoggedResult = true
    }

    fun resetLogFlag() {
        hasLoggedResult = false
    }

    fun onMessageTextChange(newText: String) {
        messageText = newText
    }

    fun checkMessage(language: String, onComplete: () -> Unit) {
        viewModelScope.launch {
            isLoading = true
            errorMessage = null
            try {
                val response = RetrofitClient.apiService.analyzeMessage(
                    AnalyzeRequest(message = messageText, language = language)
                )
                result = response
                hasLoggedResult = false
            } catch (e: Exception) {
                errorMessage = "Couldn't reach the server: ${e.message}"
            } finally {
                isLoading = false
                onComplete()
            }
        }
    }

    fun updateResult(response: AnalyzeResponse) {
        result = response
    }
}