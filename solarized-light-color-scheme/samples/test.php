<?php

namespace Trikoder\Classifieds\Njuskalo\Core\Front\Banners;

use fw3k2_db_persistent;

class Foo extends Bar
{
	public function foo ($bar, $baz)
	{

	}
}

/* Comment */
// Comment
require_once($GLOBALS['g_campsiteDir']. "/$ADMIN_DIR/country/common.php");
require_once($GLOBALS['g_campsiteDir']. "/classes/SimplePager.php");
camp_load_translation_strings("api");

$f_country_language_selected = camp_session_get('f_language_selected', '');
$f_country_offset = camp_session_get('f_country_offset', 0);
if (empty($f_country_language_selected)) {
	$f_country_language_selected = null;
}
$ItemsPerPage = 20;
$languages = Language::GetLanguages(null, null, null, array(), array(), true);
$numCountries = Country::GetNumCountries($f_country_language_selected);

$pager = new SimplePager($numCountries, $ItemsPerPage, "index.php?");

$crumbs = array();
$crumbs = [];
$crumbs[] = array(getGS("Configure"), "");
$crumbs[] = array(getGS("Countries"), "");
echo camp_html_breadcrumbs($crumbs);

var_dump(expression);
die;

?>

<?php  if ($g_user->hasPermission("ManageCountries")) { ?>
<table BORDER="0" CELLSPACING="0" CELLPADDING="1">
    <tr>
        <td><a href="add.php"><?php putGS("Add new"); ?></a></td>
    </tr>
</table>
