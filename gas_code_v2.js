function doPost(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("訂單總表");
  var data = JSON.parse(e.postData.contents);
  
  // 如果是修改狀態的請求
  if (data.action === "update_status") {
    var rows = sheet.getDataRange().getValues();
    var found = false;
    // 從後往前找匹配的單子 (日期+打手ID+老闆ID)
    for (var i = rows.length - 1; i >= 1; i--) {
      if (rows[i][0] == data.date && rows[i][1] == data.slayer_id && rows[i][3] == data.customer_id) {
        sheet.getRange(i + 1, 10).setValue(data.new_status); // 第 10 欄是結算狀態
        found = true;
        break;
      }
    }
    return ContentService.createTextOutput(found ? "Updated" : "Not Found").setMimeType(ContentService.MimeType.TEXT);
  }
  
  // 如果是新增訂單的請求
  var row = [
    data.date,
    data.slayer_id,
    data.rate_type,
    data.customer_id,
    data.item,
    data.price,
    data.discount,
    data.slayer_cut,
    data.profit,
    "待結算"
  ];
  
  sheet.appendRow(row);
  return ContentService.createTextOutput("Success").setMimeType(ContentService.MimeType.TEXT);
}
