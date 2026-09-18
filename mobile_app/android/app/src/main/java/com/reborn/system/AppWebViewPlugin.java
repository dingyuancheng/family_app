package com.reborn.system;

import android.content.Intent;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "AppWebView")
public class AppWebViewPlugin extends Plugin {

    @PluginMethod
    public void open(PluginCall call) {
        String url = call.getString("url");
        if (url == null || url.isEmpty()) {
            call.reject("Must provide a url");
            return;
        }

        String title = call.getString("title", "");

        Intent intent = new Intent(getContext(), AppWebViewActivity.class);
        intent.putExtra("url", url);
        intent.putExtra("title", title);
        getContext().startActivity(intent);

        JSObject ret = new JSObject();
        ret.put("opened", true);
        call.resolve(ret);
    }
}