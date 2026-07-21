package com.suraksha.ai.screens.home

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun HomeScreen(
    modifier: Modifier = Modifier,
    onCheckMessageClick: () -> Unit = {},
    onScanSmsClick: () -> Unit = {}
) {
    val backgroundGradient = Brush.verticalGradient(
        colors = listOf(
            Color(0xFF0D47A1),
            Color(0xFF00897B)
        )
    )

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(backgroundGradient)
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val dotSpacing = 40.dp.toPx()
            val dotRadius = 2.dp.toPx()

            var y = 0f
            while (y < size.height) {
                var x = 0f
                while (x < size.width) {
                    drawCircle(
                        color = Color.White.copy(alpha = 0.12f),
                        radius = dotRadius,
                        center = androidx.compose.ui.geometry.Offset(x, y)
                    )
                    x += dotSpacing
                }
                y += dotSpacing
            }
        }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Row {
                Text(
                    text = "सुर",
                    fontSize = 80.sp,
                    fontWeight = FontWeight.ExtraBold,
                    fontFamily = FontFamily.Serif,
                    color = Color.White
                )
                Text(
                    text = "ksha",
                    fontSize = 80.sp,
                    fontWeight = FontWeight.ExtraBold,
                    fontFamily = FontFamily.Cursive,
                    color = Color.White
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            Text(
                text = "Your shield against scams",
                fontSize = 18.sp,
                fontStyle = FontStyle.Italic,
                fontFamily = FontFamily.Serif,
                color = Color.White.copy(alpha = 0.9f)
            )

            Spacer(modifier = Modifier.height(56.dp))

            Button(
                onClick = onCheckMessageClick,
                shape = RoundedCornerShape(28.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color.White,
                    contentColor = Color(0xFF0D47A1)
                ),
                modifier = Modifier.height(56.dp)
            ) {
                Text(
                    text = "Check a Message",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = onScanSmsClick,
                shape = RoundedCornerShape(28.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color.White.copy(alpha = 0.85f),
                    contentColor = Color(0xFF0D47A1)
                ),
                modifier = Modifier.height(56.dp)
            ) {
                Text(text = "Scan SMS Inbox", fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}