package com.suraksha.ai.screens.home

import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.suraksha.ai.R


data class HomeAction(
    val label: String,
    val icon: ImageVector,
    val onClick: () -> Unit
)


@Composable
fun HomeScreen(
    modifier: Modifier = Modifier,
    onCheckMessageClick: () -> Unit = {},
    onScanSmsClick: () -> Unit = {},
    onCallUploadClick: () -> Unit = {},
    onGuardianClick: () -> Unit = {},
    onSettingsClick: () -> Unit = {},
    onProfileClick: () -> Unit = {}
) {

    val backgroundGradient = Brush.verticalGradient(
        colors = listOf(
            MaterialTheme.colorScheme.primary,
            MaterialTheme.colorScheme.secondary
        )
    )


    val actions = listOf(
        HomeAction(
            stringResource(R.string.check_message_button),
            Icons.Outlined.Chat,
            onCheckMessageClick
        ),
        HomeAction(
            stringResource(R.string.scan_sms_button),
            Icons.Outlined.MarkEmailUnread,
            onScanSmsClick
        ),
        HomeAction(
            stringResource(R.string.guardian_button),
            Icons.Outlined.Group,
            onGuardianClick
        ),
        HomeAction(
            stringResource(R.string.call_upload_button),
            Icons.Outlined.Call,
            onCallUploadClick
        )
    )


    Scaffold(
        modifier = modifier.fillMaxSize(),
        containerColor = Color.Transparent,

        bottomBar = {

            NavigationBar(
                containerColor = MaterialTheme.colorScheme.primary
            ) {

                NavigationBarItem(
                    selected = true,
                    onClick = {},
                    icon = {
                        Icon(
                            Icons.Filled.Home,
                            contentDescription = "Home"
                        )
                    },
                    label = {
                        Text(stringResource(R.string.home))
                    },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = Color.White,
                        selectedTextColor = Color.White,
                        unselectedIconColor = Color.White.copy(alpha = 0.6f),
                        unselectedTextColor =Color.White.copy(alpha = 0.6f),
                        indicatorColor = Color.White.copy(alpha = 0.15f)
                    )
                )


                NavigationBarItem(
                    selected = false,
                    onClick = onSettingsClick,
                    icon = {
                        Icon(
                            Icons.Filled.Settings,
                            contentDescription = "Settings"
                        )
                    },
                    label = {
                        Text(stringResource(R.string.settings))
                    },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = Color.White,
                        selectedTextColor = Color.White,
                        unselectedIconColor = Color.White.copy(alpha = 0.6f),
                        unselectedTextColor = Color.White.copy(alpha = 0.6f),
                        indicatorColor = Color.White.copy(alpha = 0.15f)
                    )
                )
            }
        }

    ) { innerPadding ->


        Column(
            modifier = modifier
                .fillMaxSize()
                .background(backgroundGradient)
                .padding(innerPadding)
                .padding(16.dp)
        ) {


            // Top bar
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {

                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {

                    Icon(
                        imageVector = Icons.Outlined.GppGood,
                        contentDescription = "Suraksha logo",
                        tint = Color.White,
                        modifier = Modifier.size(24.dp)
                    )


                    Spacer(modifier = Modifier.width(8.dp))


                    Row {

                        Text(
                            text = "सुर",
                            fontSize = 22.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Serif,
                            color = Color.White
                        )

                        Text(
                            text = "ksha",
                            fontSize = 22.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Cursive,
                            color = Color.White
                        )
                    }
                }


                IconButton(
                    onClick = onProfileClick
                ) {

                    Icon(
                        imageVector = Icons.Outlined.AccountCircle,
                        contentDescription = "Profile",
                        tint = Color.White
                    )
                }
            }


            Spacer(modifier = Modifier.height(24.dp))


            Text(
                text = stringResource(R.string.home_title),
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )


            Text(
                text = stringResource(R.string.home_subtitle),
                fontSize = 14.sp,
                color = Color.White.copy(alpha = 0.8f)
            )


            Spacer(modifier = Modifier.height(25.dp))


            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                contentPadding = PaddingValues(bottom = 20.dp)

            ) {


                items(actions) { action ->


                    Card(
                        onClick = action.onClick,
                        modifier = Modifier
                            .fillMaxWidth()
                            .aspectRatio(1.4f),

                        colors = CardDefaults.cardColors(
                            containerColor = Color.White.copy(alpha = 0.12f)
                        ),

                        shape = RoundedCornerShape(16.dp)

                    ) {


                        Column(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(16.dp),

                            verticalArrangement = Arrangement.SpaceBetween

                        ) {


                            Icon(
                                imageVector = action.icon,
                                contentDescription = action.label,
                                tint = Color.White
                            )


                            Text(
                                text = action.label,
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color.White
                            )
                        }
                    }
                }
            }


            Card(
                modifier = Modifier.fillMaxWidth(),

                colors = CardDefaults.cardColors(
                    containerColor =
                        MaterialTheme.colorScheme.primary.copy(alpha = 0.4f)
                ),

                shape = RoundedCornerShape(16.dp)

            ) {


                Text(
                    text = stringResource(R.string.status_safe),

                    modifier = Modifier.padding(16.dp),

                    fontSize = 14.sp,

                    fontWeight = FontWeight.Bold,

                    color = Color.White
                )
            }
        }
    }
}