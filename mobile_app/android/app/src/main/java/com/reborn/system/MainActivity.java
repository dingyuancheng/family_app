package com.reborn.system;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(AppWebViewPlugin.class);
        super.onCreate(savedInstanceState);
    }
}