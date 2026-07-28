package com.suraksha.ai.screens.splash

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.size
import androidx.compose.material3.MaterialTheme
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.material.icons.Icons
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.material.icons.filled.GppGood
import androidx.compose.foundation.shape.RoundedCornerShape

@Composable
fun SplashScreen(onSplashFinished: () -> Unit) {
    LaunchedEffect(Unit) {
        delay(1200)
        onSplashFinished()
    }

    val backgroundGradient = Brush.verticalGradient(
        colors = listOf(MaterialTheme.colorScheme.primary,
            MaterialTheme.colorScheme.secondary)
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(backgroundGradient),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Box(
                modifier = Modifier
                    .size(120.dp)
                    .background(Color.White.copy(alpha = 0.15f), RoundedCornerShape(28.dp)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Filled.GppGood,
                    contentDescription = "Suraksha shield",
                    tint = Color.White,
                    modifier = Modifier.size(70.dp)
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            Row {
                Text(
                    text = "सुर",
                    fontSize = 56.sp,
                    fontWeight = FontWeight.ExtraBold,
                    fontFamily = FontFamily.Serif,
                    color = Color.White
                )
                Text(
                    text = "ksha",
                    fontSize = 56.sp,
                    fontWeight = FontWeight.ExtraBold,
                    fontFamily = FontFamily.Cursive,
                    color = Color.White
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "Your shield against scams",
                fontSize = 19.sp,
                color = Color.White.copy(alpha = 0.85f),
                fontStyle = FontStyle.Italic,
                fontFamily = FontFamily.Serif
            )
        }
    }
}