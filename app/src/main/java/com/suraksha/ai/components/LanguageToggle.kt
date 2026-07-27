package com.suraksha.ai.components
import androidx.compose.ui.res.stringResource
import android.app.Activity
import androidx.appcompat.app.AppCompatDelegate
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.os.LocaleListCompat

@Composable
fun LanguageToggle(modifier: Modifier = Modifier) {
    val context = LocalContext.current

    fun setAppLanguage(languageCode: String) {
        val appLocale = LocaleListCompat.forLanguageTags(languageCode)
        AppCompatDelegate.setApplicationLocales(appLocale)
        (context as? Activity)?.recreate()
    }

    Row(modifier = modifier) {
        Button(
            onClick = { setAppLanguage("en") },
            colors = ButtonDefaults.buttonColors(containerColor = Color.White.copy(alpha = 0.2f))
        ) {
            Text("EN", color = Color.White)
        }

        Spacer(modifier = Modifier.width(8.dp))

        Button(
            onClick = { setAppLanguage("hi") },
            colors = ButtonDefaults.buttonColors(containerColor = Color.White.copy(alpha = 0.2f))
        ) {
            Text("हि", color = Color.White)
        }

        Spacer(modifier = Modifier.width(8.dp))

        Button(
            onClick = { setAppLanguage("gu") },
            colors = ButtonDefaults.buttonColors(containerColor = Color.White.copy(alpha = 0.2f))
        ) {
            Text("ગુ", color = Color.White)
        }
    }
}