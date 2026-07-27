package com.suraksha.ai.screens.guardian

import android.app.Application
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import org.json.JSONArray
import org.json.JSONObject
import androidx.compose.ui.res.stringResource
data class Guardian(val name: String, val relation: String, val phone: String)

class GuardianViewModel(application: Application) : AndroidViewModel(application) {

    private val prefs = application.getSharedPreferences("suraksha_prefs", 0)

    var guardians by mutableStateOf<List<Guardian>>(emptyList())
        private set

    var contactName by mutableStateOf("")
        private set

    var contactRelation by mutableStateOf("")
        private set

    var contactPhone by mutableStateOf("")
        private set

    var alertsEnabled by mutableStateOf(prefs.getBoolean("alerts_enabled", true))
        private set

    fun updateAlertsEnabled(enabled: Boolean) {
        alertsEnabled = enabled
        prefs.edit().putBoolean("alerts_enabled", enabled).apply()
    }



    init {
        loadGuardians()
    }


    fun onContactNameChange(newValue: String) { contactName = newValue }
    fun onContactRelationChange(newValue: String) { contactRelation = newValue }
    fun onContactPhoneChange(newValue: String) { contactPhone = newValue }

    fun addGuardian() {
        if (contactName.isNotBlank() && contactPhone.isNotBlank()) {
            val newGuardian = Guardian(contactName, contactRelation, contactPhone)
            guardians = guardians + newGuardian
            saveGuardians()
            contactName = ""
            contactRelation = ""
            contactPhone = ""
        }
    }

    fun removeGuardian(guardian: Guardian) {
        guardians = guardians.filter { it != guardian }
        saveGuardians()
    }

    fun hasContact(): Boolean {
        return guardians.isNotEmpty()
    }
    enum class AlertResult { NO_GUARDIANS, NO_PERMISSION, SUCCESS, FAILED }

    fun sendAlert(
        message: String,
        context: android.content.Context,
        onResult: (AlertResult, Int, String?) -> Unit
    ) {
        if (guardians.isEmpty()) {
            onResult(AlertResult.NO_GUARDIANS, 0, null)
            return
        }

        val hasPermission = androidx.core.content.ContextCompat.checkSelfPermission(
            context,
            android.Manifest.permission.SEND_SMS
        ) == android.content.pm.PackageManager.PERMISSION_GRANTED

        if (!hasPermission) {
            onResult(AlertResult.NO_PERMISSION, 0, null)
            return
        }

        try {
            val smsManager = android.telephony.SmsManager.getDefault()
            guardians.forEach { guardian ->
                smsManager.sendTextMessage(guardian.phone, null, message, null, null)
            }
            onResult(AlertResult.SUCCESS, guardians.size, null)
        } catch (e: Exception) {
            onResult(AlertResult.FAILED, 0, e.message)
        }
    }

    fun sendTestAlert(
        context: android.content.Context,
        onResult: (AlertResult, Int, String?) -> Unit
    ) {
        val testMessage = "This is a test alert from Suraksha. If this were a real scam detection, your family member would be notified like this."
        sendAlert(testMessage, context, onResult)
    }

    private fun saveGuardians() {
        val jsonArray = JSONArray()
        guardians.forEach { guardian ->
            val obj = JSONObject()
            obj.put("name", guardian.name)
            obj.put("relation", guardian.relation)
            obj.put("phone", guardian.phone)
            jsonArray.put(obj)
        }
        prefs.edit().putString("guardians", jsonArray.toString()).apply()
    }

    private fun loadGuardians() {
        val jsonString = prefs.getString("guardians", null) ?: return
        val jsonArray = JSONArray(jsonString)
        val loaded = mutableListOf<Guardian>()
        for (i in 0 until jsonArray.length()) {
            val obj = jsonArray.getJSONObject(i)
            loaded.add(Guardian(obj.getString("name"), obj.getString("relation"), obj.getString("phone")))
        }
        guardians = loaded
    }
}