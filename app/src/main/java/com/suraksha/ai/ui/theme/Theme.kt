package com.suraksha.ai.ui.theme

import android.os.Build
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color


//Dark Color Scheme
private val DarkColorScheme = darkColorScheme(
    primary = SurakshaDarkBlue,
    secondary = SurakshaDarkTeal,
    tertiary = SurakshaBlue,

    background = Color(0xFF020B14),
    surface = Color(0xFF081A29),

    onBackground = Color(0xFFF3F7FA),
    onSurface = Color(0xFFF3F7FA)
)

//Light color Scheme
private val LightColorScheme = lightColorScheme(
    primary = SurakshaBlue,
    secondary = SurakshaTeal,
    tertiary = SurakshaBlue,

    background = Color(0xFFD9EAF7),
    surface = Color(0xFFEDF5FA),

    onBackground = Color(0xFF1B2A34),
    onSurface = Color(0xFF1B2A34)
)


@Composable
fun SurakshaTheme(
    darkTheme: Boolean = AppThemeState.isDarkMode,
    content: @Composable () -> Unit
) {

    val colorScheme = if (darkTheme) {
        DarkColorScheme
    } else {
        LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}