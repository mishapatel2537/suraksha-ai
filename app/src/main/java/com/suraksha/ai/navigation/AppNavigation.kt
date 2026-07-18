package com.suraksha.ai.navigation


import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.suraksha.ai.screens.home.HomeScreen
import com.suraksha.ai.screens.messagecheck.MessageInputScreen

@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "home") {
        composable("home") {
            HomeScreen(
                onCheckMessageClick = {
                    navController.navigate("messageInput")
                }
            )
        }
        composable("messageInput") {
            MessageInputScreen()
        }
    }
}