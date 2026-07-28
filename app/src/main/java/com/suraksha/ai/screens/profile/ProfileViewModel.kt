package com.suraksha.ai.screens.profile

import android.app.Application
import androidx.compose.ui.res.stringResource
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import org.json.JSONArray
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

data class ActivityEntry(val label: String, val riskLevel: String, val date: String)

class ProfileViewModel(application: Application) : AndroidViewModel(application) {

    private val prefs = application.getSharedPreferences("suraksha_prefs", 0)

    var userName by mutableStateOf("")
        private set

    var memberSince by mutableStateOf("")
        private set

    var activityLog by mutableStateOf<List<ActivityEntry>>(emptyList())
        private set

    // New state
    var phoneNumber by mutableStateOf(prefs.getString("phone_number", "") ?: "")
        private set

    var isLoggedIn by mutableStateOf(prefs.getBoolean("is_logged_in", false))
        private set

    fun onPhoneChange(newPhone: String) {
        phoneNumber = newPhone
        prefs.edit().putString("phone_number", newPhone).apply()
    }

    fun completeLogin() {
        isLoggedIn = true
        prefs.edit().putBoolean("is_logged_in", true).apply()
    }
    fun logout() {
        isLoggedIn = false
        prefs.edit().putBoolean("is_logged_in", false).apply()
    }
    init {
        userName = prefs.getString("user_name", "Guest") ?: "Guest"

        val savedDate = prefs.getString("member_since", null)
        if (savedDate == null) {
            val today = SimpleDateFormat("MMM yyyy", Locale.ENGLISH).format(Date())
            prefs.edit().putString("member_since", today).apply()
            memberSince = today
        } else {
            memberSince = savedDate
        }

        loadActivityLog()
    }

    fun onNameChange(newName: String) {
        userName = newName
        prefs.edit().putString("user_name", newName).apply()
    }

    fun addActivityEntry(label: String, riskLevel: String) {
        val date = SimpleDateFormat("dd MMM, hh:mm a", Locale.ENGLISH).format(Date())
        val newEntry = ActivityEntry(label, riskLevel, date)
        activityLog = (listOf(newEntry) + activityLog).take(10)
        saveActivityLog()
    }

    fun messagesCheckedCount(): Int = activityLog.count { it.label == "Message" }
    fun callsCheckedCount(): Int = activityLog.count { it.label == "Call" }

    private fun saveActivityLog() {
        val jsonArray = JSONArray()
        activityLog.forEach { entry ->
            val obj = JSONObject()
            obj.put("label", entry.label)
            obj.put("riskLevel", entry.riskLevel)
            obj.put("date", entry.date)
            jsonArray.put(obj)
        }
        prefs.edit().putString("activity_log", jsonArray.toString()).apply()
    }

    private fun loadActivityLog() {
        val jsonString = prefs.getString("activity_log", null) ?: return
        val jsonArray = JSONArray(jsonString)
        val loaded = mutableListOf<ActivityEntry>()
        for (i in 0 until jsonArray.length()) {
            val obj = jsonArray.getJSONObject(i)
            loaded.add(ActivityEntry(obj.getString("label"), obj.getString("riskLevel"), obj.getString("date")))
        }
        activityLog = loaded
    }
    fun clearActivityData() {
        activityLog = emptyList()

        prefs.edit()
            .remove("activity_log")
            .apply()
    }
}