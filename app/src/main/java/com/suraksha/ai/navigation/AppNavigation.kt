package com.suraksha.ai.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.suraksha.ai.screens.home.HomeScreen
import com.suraksha.ai.screens.messagecheck.MessageInputScreen
import com.suraksha.ai.screens.messagecheck.MessageInputViewModel
import com.suraksha.ai.screens.result.ResultScreen
import com.suraksha.ai.screens.sms.SmsPermissionScreen
import com.suraksha.ai.screens.sms.SmsInboxScreen
import com.suraksha.ai.screens.splash.SplashScreen
import com.suraksha.ai.screens.callupload.CallUploadScreen
import com.suraksha.ai.screens.guardian.GuardianScreen
import com.suraksha.ai.screens.profile.ProfileScreen
import com.suraksha.ai.screens.settings.SettingsScreen
import com.suraksha.ai.screens.profile.ProfileViewModel

@Composable
fun AppNavigation(sharedText: String? = null) {
    val navController = rememberNavController()
    val profileViewModel: ProfileViewModel = androidx.lifecycle.viewmodel.compose.viewModel()
    val sharedViewModel: MessageInputViewModel = androidx.lifecycle.viewmodel.compose.viewModel()

    NavHost(
        navController = navController,
        startDestination = "splash"
    ) {
        composable("splash") {
            SplashScreen(
                onSplashFinished = {
                    navController.navigate(if (sharedText != null) "messageInput" else "home") {
                        popUpTo("splash") { inclusive = true }
                    }
                }
            )
        }
        composable("home") {
            HomeScreen(
                onCheckMessageClick = {
                    navController.navigate("messageInput")
                },
                onScanSmsClick = {
                    navController.navigate("smsPermission")
                },
                onCallUploadClick = { navController.navigate("callUpload") },
                onSettingsClick = { navController.navigate("settings") },
                onProfileClick = { navController.navigate("profile") },
                onGuardianClick = { navController.navigate("guardian") }

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
                if (!sharedViewModel.hasLoggedResult) {
                    profileViewModel.addActivityEntry("Message", result.riskLevel)
                    sharedViewModel.markResultLogged()
                }
                ResultScreen(result = result)
            }
        }
        composable("smsPermission") {
            SmsPermissionScreen(
                onPermissionGranted = {
                    navController.navigate("smsInbox") {
                        popUpTo("smsPermission") { inclusive = true }
                    }
                }
            )
        }
        composable("smsInbox") {
            SmsInboxScreen()
        }
        composable("callUpload") {
            CallUploadScreen(
                onResultReady = { result ->
                    sharedViewModel.updateResult(result)
                    profileViewModel.addActivityEntry("Call", result.riskLevel)
                    navController.navigate("result")
                }
            )
        }
        composable("guardian") {
            GuardianScreen()
        }
        composable("profile") {
            ProfileScreen(
                viewModel = profileViewModel,
                onSettingsClick = { navController.navigate("settings") }
            )
        }
        composable("settings") {
            SettingsScreen()
        }

    }
}