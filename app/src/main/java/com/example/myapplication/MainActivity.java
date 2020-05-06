
package com.example.myapplication;

import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.ContentResolver;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;
import android.widget.ListView;
import android.widget.SimpleAdapter;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.google.gson.Gson;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class MainActivity extends AppCompatActivity {
    private WebView webView=null;
    private List<Map<String, Object>> all_data;
    private String data;
    public static final int REQ_CODE_CONTACT = 1;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        getSupportActionBar().hide();
        all_data = new ArrayList<Map<String, Object>>();
        webView = (WebView) findViewById(R.id.webview);
        // 启用javascript
        webView.getSettings().setJavaScriptEnabled(true);
        // 从assets目录下面的加载html
        webView.loadUrl("file:///android_asset/index.html");
        webView.addJavascriptInterface(MainActivity.this,"android");
    }

    @JavascriptInterface
    public void readSMS(){
        data="";
        all_data.clear();
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                checkSMSPermission();
                Gson gson = new Gson();
                String jsondata = gson.toJson(all_data);
                SendGetMessage(jsondata);

            }
        });
    }

    private void checkSMSPermission() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_SMS) != PackageManager.PERMISSION_GRANTED)
        {//未获取到读取短信权限,向系统申请权限
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.READ_SMS},REQ_CODE_CONTACT);
        }
        else
            query();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        //判断用户是否，同意 获取短信授权
        //获取到读取短信权限
        if (requestCode == REQ_CODE_CONTACT && grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED)
            query();
        else
            Toast.makeText(this, "未获取到短信权限", Toast.LENGTH_SHORT).show();
    }

    private void query()
    {//读取所有短信
        Uri uri = Uri.parse("content://sms/");
        ContentResolver resolver = getContentResolver();
        Cursor cursor = resolver.query(uri, new String[]{"_id", "address", "body", "date", "type"}, null, null, null);
        if (cursor != null && cursor.getCount() > 0) {
            int _id;
            String address;
            String body;
            String date;
            int type;
            while (cursor.moveToNext())
            {
                Map<String, Object> map = new HashMap<String, Object>();
                _id = cursor.getInt(0);
                address = cursor.getString(1);
                body = cursor.getString(2);
                date = cursor.getString(3);
                type = cursor.getInt(4);
                map.put("num", address);
                map.put("message", body);
                Log.i("alldata", "_id=" + _id + " address=" + address + " body=" + body + " date=" + date + " type=" + type);
                if (type == 1)
                    all_data.add(map);
            }
            Log.i("recedata", String.valueOf(all_data));
        }
    }

    public void SendGetMessage(final String json) {
        new Thread()
        {
            @Override
            public void run() {
                String result="";
                BufferedReader reader = null;
                try {
                    URL url = new URL("http://192.168.1.17:5001");
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("POST");
                    conn.setDoOutput(true);
                    conn.setDoInput(true);
                    conn.setUseCaches(false);
                    conn.setRequestProperty("Connection", "Keep-Alive");
                    conn.setRequestProperty("Charset", "UTF-8");
                    // 设置文件类型:
                    conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
                    // 设置接收类型否则返回415错误
                    conn.setRequestProperty("accept", "application/json");
                    // 往服务器里面发送数据
                    if (json != null && !TextUtils.isEmpty(json))
                    {
                        byte[] writebytes = json.getBytes();
                        // 设置文件长度
                        conn.setRequestProperty("Content-Le4ngth", String.valueOf(writebytes.length));
                        OutputStream outwritestream = conn.getOutputStream();
                        outwritestream.write(json.getBytes());
                        outwritestream.flush();
                        outwritestream.close();
                        Log.d("connect", ""+conn.getResponseCode());
                    }
                    if (conn.getResponseCode() == 200)
                    {
                        reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                        result = reader.readLine();
                        Log.i("response", result);
                        finalData(result);
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                } finally {
                    if (reader != null) {
                        try {
                            reader.close();
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }
                }
            }
        }.start();
    }

    private void finalData(String final_data)
    {
            data=final_data;
            Log.i("testfinal", data);
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    showMessage();
                }
            });
    }

    public void showMessage()
    {
        String call = "javascript:show('" + data  + "')";
        webView.loadUrl(call);
    }
}
