<?php
/**
 * 酷9 绝对兼容版接口
 * 去除了 #EXTM3U 头，去除了所有可能产生干扰的缓冲
 */

// 1. 强制清除所有输出缓冲 (防止空格、报错信息干扰)
while (ob_get_level() > 0) {
    ob_end_clean();
}

// 2. 强制设置头部
header('Content-Type: text/plain; charset=utf-8');
header('Cache-Control: no-cache');

// 3. 引入数据库配置
require_once $_SERVER['DOCUMENT_ROOT'] . '/include/db.config.php';

// 4. 连接数据库
$conn = new mysqli(DB_HOST, DB_USER, DB_PASSWD, DB_NAME, null, DB_SOCKET);

if ($conn->connect_error) {
    // 如果数据库连不上，直接输出错误文本，不要带 HTML 标签
    die("DB Connection Error");
}
$conn->set_charset("utf8");

// 5. 获取动作
$action = isset($_GET['action']) ? $_GET['action'] : 'list';

if ($action === 'list') {
    outputChannelList($conn);
} elseif ($action === 'search') {
    searchChannel($conn);
}

$conn->close();

/**
 * 输出列表 (无 #EXTM3U 头版本)
 */
function outputChannelList($conn) {
    $table_cat = DB_PRE . 'category';
    $table_ch = DB_PRE . 'channels';

    // 查询分类
    $sql_cat = "SELECT name, psw FROM {$table_cat} WHERE enable = 1 ORDER BY id ASC";
    $result_cat = $conn->query($sql_cat);

    if (!$result_cat || $result_cat->num_rows === 0) {
        // 没数据直接结束，不要输出 #EXTM3U
        return; 
    }

    // 注意：这里不再输出 #EXTM3U

    while ($cat = $result_cat->fetch_assoc()) {
        $catName = $cat['name'];
        $catPsw = $cat['psw'] ?? '';
        
        // 拼接分类名
        $groupTitle = $catName;
        if (!empty($catPsw)) {
            $groupTitle .= '_' . $catPsw;
        }
        
        // 输出分类头
        echo $groupTitle . ",#genre#\n";

        // 查询频道
        $sql_ch = "SELECT name, url FROM {$table_ch} WHERE category = ? ORDER BY id ASC";
        $stmt = $conn->prepare($sql_ch);
        $stmt->bind_param("s", $catName);
        $stmt->execute();
        $result_ch = $stmt->get_result();

        if ($result_ch && $result_ch->num_rows > 0) {
            while ($ch = $result_ch->fetch_assoc()) {
                if (!empty($ch['name']) && !empty($ch['url'])) {
                    echo $ch['name'] . "," . $ch['url'] . "\n";
                }
            }
        }
        // 分类之间空一行
        echo "\n";
    }
}

/**
 * 搜索函数
 */
function searchChannel($conn) {
    $keyword = isset($_GET['keyword']) ? trim($_GET['keyword']) : '';
    
    if (empty($keyword)) {
        return;
    }

    $table_ch = DB_PRE . 'channels';
    $sql = "SELECT name, url, category FROM {$table_ch} WHERE name LIKE ? ORDER BY id ASC";
    
    $stmt = $conn->prepare($sql);
    $like_keyword = "%{$keyword}%";
    $stmt->bind_param("s", $like_keyword);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if ($result && $result->num_rows > 0) {
        while ($ch = $result->fetch_assoc()) {
            echo $ch['name'] . "," . $ch['url'] . "\n";
        }
    }
}
?>
