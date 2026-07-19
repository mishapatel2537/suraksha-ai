package com.suraksha.ai.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.suraksha.ai.screens.home.HomeScreen
import com.suraksha.ai.screens.messagecheck.MessageInputScreen
import com.suraksha.ai.screens.messagecheck.MessageInputViewModel
import com.suraksha.ai.screens.result.ResultScreen

@Composable
fun AppNavigation(sharedText: String? = null) {
    val navController = rememberNavController()
    val sharedViewModel: MessageInputViewModel = androidx.lifecycle.viewmodel.compose.viewModel()

    NavHost(
        navController = navController,
        startDestination = if (sharedText != null) "messageInput" else "home"
    ) {
        composable("home") {
            HomeScreen(
                onCheckMessageClick = {
                    navController.navigate("messageInput")
                }
            )
        }
        composable("messageInput") {
            MessageInputScreen(
                initialText = sharedText ?: "",
                viewModel = sharedViewModel,
                onCheckMessageClick = {
                    navController.navigate("result")
                }
            )
        }
        composable("result") {
            sharedViewModel.result?.let { result ->
                ResultScreen(result = result)
            }
        }
    }
}