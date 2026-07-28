package com.suraksha.ai.screens.settings

import androidx.compose.ui.res.stringResource
import com.suraksha.ai.R
import androidx.compose.foundation.background
import androidx.compose.material3.MaterialTheme
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.suraksha.ai.components.LanguageToggle
import com.suraksha.ai.ui.theme.AppThemeState
import com.suraksha.ai.screens.guardian.GuardianViewModel
import com.suraksha.ai.screens.profile.ProfileViewModel

@Composable
fun SettingsScreen(
    modifier: Modifier = Modifier,
    guardianViewModel: GuardianViewModel,
    profileViewModel: ProfileViewModel,
    navController: NavController

) {
    var dataCleared by remember { mutableStateOf(false) }

    val backgroundGradient = Brush.verticalGradient(
        colors = listOf(MaterialTheme.colorScheme.primary,
            MaterialTheme.colorScheme.secondary)
    )

    val switchColors = SwitchDefaults.colors(
        checkedThumbColor = Color.White,
        checkedTrackColor = MaterialTheme.colorScheme.secondary,
        uncheckedThumbColor = Color.White,
        uncheckedTrackColor = Color.White.copy(alpha = 0.3f)
    )

    val dividerColor = Color.White.copy(alpha = 0.25f)


    Column(
        modifier = modifier
            .fillMaxSize()
            .background(backgroundGradient)
            .padding(24.dp)
    ) {
        Text(
                text = stringResource(R.string.settings_title),
            fontSize = 26.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )

        Spacer(modifier = Modifier.height(20.dp))
        Divider(color = dividerColor)
        Spacer(modifier = Modifier.height(20.dp))

        Text(text = stringResource(R.string.language_label), fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.White)
        Spacer(modifier = Modifier.height(8.dp))
        LanguageToggle()

        Spacer(modifier = Modifier.height(20.dp))
        Divider(color = dividerColor)
        Spacer(modifier = Modifier.height(20.dp))


        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(text = stringResource(R.string.guardian_alerts_title), fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.White)
                Text(
                    text = stringResource(R.string.guardian_alerts_desc),
                    fontSize = 12.sp,
                    color = Color.White.copy(alpha = 0.8f)
                )
            }
            Switch(
                checked = guardianViewModel.alertsEnabled,
                onCheckedChange = { guardianViewModel.updateAlertsEnabled(it) },
                colors = switchColors
            )
        }

        Spacer(modifier = Modifier.height(20.dp))
        Divider(color = dividerColor)
        Spacer(modifier = Modifier.height(20.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(text = stringResource(R.string.dark_mode_label), fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.White)
            Switch(
                checked = AppThemeState.isDarkMode,
                onCheckedChange = { AppThemeState.isDarkMode = it },
                colors = switchColors
            )
        }

        Spacer(modifier = Modifier.height(20.dp))
        Divider(color = dividerColor)
        Spacer(modifier = Modifier.height(20.dp))

        Text(text = stringResource(R.string.data_label), fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.White)
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = { profileViewModel.clearActivityData()
                dataCleared = true },
            shape = RoundedCornerShape(20.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color.White.copy(alpha = 0.15f),
                contentColor = Color.White
            )
        ) {
            Text(stringResource(R.string.clear_activity_button))
        }
        if (dataCleared) {
            Spacer(modifier = Modifier.height(6.dp))
            Text(text = stringResource(R.string.activity_cleared_confirm), fontSize = 12.sp, color = Color(0xFFA5D6A7))
        }

        Button(
            onClick = {
                profileViewModel.logout()
                navController.navigate("login") {
                    popUpTo(0) { inclusive = true }
                }
            },
            shape = RoundedCornerShape(20.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color.White.copy(alpha = 0.15f),
                contentColor = Color.White
            )
        ) {
            Text(stringResource(R.string.log_out_button))
        }

        Spacer(modifier = Modifier.height(20.dp))
        Divider(color = dividerColor)
        Spacer(modifier = Modifier.height(20.dp))

        Text(text =  stringResource(R.string.about_suraksha_title), fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.White)
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text =  stringResource(R.string.about_suraksha_body),
            fontSize = 14.sp,
            color = Color.White.copy(alpha = 0.9f)
        )

        Spacer(modifier = Modifier.height(16.dp))
        Text(text =  stringResource(R.string.app_version), fontSize = 12.sp, color = Color.White.copy(alpha = 0.6f))
    }
}