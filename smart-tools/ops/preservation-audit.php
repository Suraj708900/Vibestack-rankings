<?php
if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
$pub=dirname(__DIR__);$baseline=dirname($pub).'/v4-backups-20261101/restore-check/public_html';
if(!is_file($baseline.'/index.html'))throw new RuntimeException('Verified baseline missing');
$checked=0;$changed=[];$missing=[];
$it=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($baseline,FilesystemIterator::SKIP_DOTS));
foreach($it as $f){if(!$f->isFile()||$f->isLink())continue;$rel=substr($f->getPathname(),strlen($baseline)+1);if(str_starts_with($rel,'preview/')||str_starts_with($rel,'.private/')||preg_match('~(^|/)\.~',$rel))continue;if(!preg_match('/\.(html|css|js|php|json|xml|txt)$/i',$rel))continue;$checked++;if(!is_file($pub.'/'.$rel))$missing[]=$rel;elseif(hash_file('sha256',$pub.'/'.$rel)!==hash_file('sha256',$f->getPathname()))$changed[]=$rel;}
$manifest=json_decode(file_get_contents($pub.'/.private/v4-production-manifest.json'),true,512,JSON_THROW_ON_ERROR);$new=0;$same=0;$conflicts=[];
foreach($manifest as $rel=>$sha){if(!preg_match('~^(tools/|assets/smart-tools-v4/|tools-sitemap\.xml$)~',$rel)||str_contains($rel,'..'))throw new RuntimeException('Unsafe candidate path');if(!file_exists($pub.'/'.$rel))$new++;elseif(is_file($pub.'/'.$rel)&&hash_file('sha256',$pub.'/'.$rel)===$sha)$same++;else $conflicts[]=$rel;}
$critical=[];foreach(['index.html','api/auth.php','api/account.php','api/dashboard.php','api/ai.php','login.html','account.html','privacy.html','terms.html','about.html','contact.html','ads.txt','consent.js'] as $rel){if(is_file($baseline.'/'.$rel))$critical[$rel]=is_file($pub.'/'.$rel)&&hash_file('sha256',$pub.'/'.$rel)===hash_file('sha256',$baseline.'/'.$rel);}
$out=['audit'=>'read-only','production_files_compared'=>$checked,'missing_count'=>count($missing),'changed_count'=>count($changed),'changed_public_files'=>array_slice($changed,0,30),'missing_public_files'=>array_slice($missing,0,30),'critical_files_unchanged'=>$critical,'production_candidate'=>['new_files'=>$new,'identical_files'=>$same,'conflicts'=>$conflicts,'deployed'=>false]];
file_put_contents($pub.'/.private/v4-preservation-audit.json',json_encode($out,JSON_PRETTY_PRINT));echo json_encode($out);
