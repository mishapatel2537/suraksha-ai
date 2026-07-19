package com.suraksha.ai.screens.messagecheck

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.suraksha.ai.network.MockApiService
import com.suraksha.ai.network.models.AnalyzeResponse
import kotlinx.coroutines.launch

class MessageInputViewModel : ViewModel() {
    var messageText by mutableStateOf("")
        private set

    var result by mutableStateOf<AnalyzeResponse?>(null)
        private set

    var isLoading by mutableStateOf(false)
        private set

    fun onMessageTextChange(newText: String) {
        messageText = newText
    }

    fun checkMessage(onComplete: () -> Unit) {
        viewModelScope.launch {
            isLoading = true
            result = MockApiService.analyzeMessage(messageText)
            isLoading = false
            onComplete()
        }
    }
}