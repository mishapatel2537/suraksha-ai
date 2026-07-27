package com.suraksha.ai.screens.guardian
import androidx.compose.ui.res.stringResource
import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import com.suraksha.ai.R

@Composable
fun GuardianScreen(
    modifier: Modifier = Modifier,
    viewModel: GuardianViewModel = viewModel()
) {
    val context = LocalContext.current
    var alertMessage by remember { mutableStateOf<String?>(null) }

    val noGuardiansMsg = stringResource(R.string.guardian_alert_no_guardians)
    val noPermissionMsg = stringResource(R.string.guardian_alert_no_permission)
    val deniedMsg = stringResource(R.string.guardian_alert_denied)
    val successTemplate = stringResource(R.string.guardian_alert_success)
    val failedTemplate = stringResource(R.string.guardian_alert_failed)

    fun handleResult(result: GuardianViewModel.AlertResult, count: Int, error: String?) {
        alertMessage = when (result) {
            GuardianViewModel.AlertResult.NO_GUARDIANS -> noGuardiansMsg
            GuardianViewModel.AlertResult.NO_PERMISSION -> noPermissionMsg
            GuardianViewModel.AlertResult.SUCCESS -> successTemplate.replace("%1\$d", count.toString())
            GuardianViewModel.AlertResult.FAILED -> failedTemplate.replace("%1\$s", error ?: "")
        }
    }

    val smsPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) {
            viewModel.sendTestAlert(context) { result, count, error -> handleResult(result, count, error) }
        } else {
            alertMessage = deniedMsg
        }
    }

    val backgroundGradient = Brush.verticalGradient(
        colors = listOf(Color(0xFF0D47A1), Color(0xFF00897B))
    )

    val fieldColors = OutlinedTextFieldDefaults.colors(
        focusedBorderColor = Color.White,
        unfocusedBorderColor = Color.White.copy(alpha = 0.5f),
        focusedLabelColor = Color.White,
        unfocusedLabelColor = Color.White.copy(alpha = 0.8f),
        focusedTextColor = Color.White,
        unfocusedTextColor = Color.White,
        cursorColor = Color.White
    )

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(backgroundGradient)
            .padding(24.dp)
    ) {
        Text(
            text = stringResource(R.string.guardian_title),
            fontSize = 26.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = stringResource(R.string.guardian_subtitle),
            fontSize = 14.sp,
            color = Color.White.copy(alpha = 0.9f)
        )

        Spacer(modifier = Modifier.height(20.dp))

        OutlinedTextField(
            value = viewModel.contactName,
            onValueChange = { viewModel.onContactNameChange(it) },
            label = { Text(stringResource(R.string.guardian_name_label)) },
            modifier = Modifier.fillMaxWidth(),
            colors = fieldColors
        )

        Spacer(modifier = Modifier.height(10.dp))

        OutlinedTextField(
            value = viewModel.contactRelation,
            onValueChange = { viewModel.onContactRelationChange(it) },
            label = { Text(stringResource(R.string.guardian_relation_label)) },
            modifier = Modifier.fillMaxWidth(),
            colors = fieldColors
        )

        Spacer(modifier = Modifier.height(10.dp))

        OutlinedTextField(
            value = viewModel.contactPhone,
            onValueChange = { newValue ->
                val filtered = newValue.filter { it.isDigit() }.take(10)
                viewModel.onContactPhoneChange(filtered)
            },
            label = { Text(stringResource(R.string.guardian_phone_label)) },
            modifier = Modifier.fillMaxWidth(),
            colors = fieldColors,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone)
        )

        Spacer(modifier = Modifier.height(12.dp))

        Button(
            onClick = { viewModel.addGuardian() },
            shape = RoundedCornerShape(20.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color.White,
                contentColor = Color(0xFF0D47A1)
            )
        ) {
            Text(stringResource(R.string.guardian_add_button), fontWeight = FontWeight.Bold)
        }

        Spacer(modifier = Modifier.height(12.dp))

        Button(
            onClick = {
                val hasPermission = ContextCompat.checkSelfPermission(
                    context,
                    Manifest.permission.SEND_SMS
                ) == PackageManager.PERMISSION_GRANTED

                if (hasPermission) {
                    viewModel.sendTestAlert(context) { result, count, error -> handleResult(result, count, error) }
                } else {
                    smsPermissionLauncher.launch(Manifest.permission.SEND_SMS)
                }
            },
            shape = RoundedCornerShape(20.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color.White.copy(alpha = 0.85f),
                contentColor = Color(0xFF0D47A1)
            )
        ) {
            Text(stringResource(R.string.guardian_test_alert_button), fontWeight = FontWeight.Bold)
        }

        alertMessage?.let { msg ->
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = msg, fontSize = 13.sp, color = Color.White)
        }

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            text = stringResource(R.string.guardian_saved_title),
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )

        Spacer(modifier = Modifier.height(8.dp))

        if (viewModel.guardians.isEmpty()) {
            Text(
                text = stringResource(R.string.guardian_empty),
                fontSize = 14.sp,
                color = Color.White.copy(alpha = 0.7f)
            )
        } else {
            val separatorTemplate = stringResource(R.string.guardian_relation_phone_separator)
            val removeDesc = stringResource(R.string.guardian_remove_desc)

            LazyColumn {
                items(viewModel.guardians) { guardian ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 6.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = Color.White.copy(alpha = 0.12f)
                        ),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column {
                                Text(
                                    text = guardian.name,
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                                Text(
                                    text = separatorTemplate
                                        .replace("%1\$s", guardian.relation)
                                        .replace("%2\$s", guardian.phone),
                                    fontSize = 13.sp,
                                    color = Color.White.copy(alpha = 0.8f)
                                )
                            }
                            IconButton(onClick = { viewModel.removeGuardian(guardian) }) {
                                Icon(
                                    imageVector = Icons.Filled.Delete,
                                    contentDescription = removeDesc,
                                    tint = Color.White
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}