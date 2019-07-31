import { Component, OnInit } from '@angular/core';
import { FossService } from '../_service/foss.service';
import { TutorialsService } from '../_service/tutorials.service'

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.sass']
})
export class HomeComponent implements OnInit {

  public fossCategories;
  public currentCategory = -1;
  public currentCategoryLanguages;
  public tutorials;
  public description: string = '';
  public langData: any;
  public local_fossId: any;
  public local_langId: any;
  public local_fossIndex: any;

  constructor(
    public fossService: FossService,
    public tutorialService: TutorialsService
  ) { }

  public onFossCategoryChange(index) {
    this.currentCategory = index;
    this.description = this.fossCategories[index]['foss_category']['description'];
    this.currentCategoryLanguages = this.fossCategories[index]['languages'];

    this.tutorials = [];
  }

  public getFossCategoryLanguages() {
    if (this.currentCategory === -1) return [];
    else {
      return this.fossCategories[this.currentCategory]['languages'];
    }
  }

  public onLanguageChange(index) {
    const fossCategoryLanguages = this.getFossCategoryLanguages();

    if (fossCategoryLanguages.length !== 0) {
      const fossId = this.fossCategories[this.currentCategory]['foss_category']['id'];
      const languageId = fossCategoryLanguages[index]['id'];

      this.tutorialService.getFossTutorials(fossId, languageId).subscribe(
        (res) => this.tutorials = res,
        console.error
      );
    }
  }

  public fetchAllFoss() {
    this.fossService.getAllFossCategories().subscribe(
      (res) => {
        this.fossCategories = res['data'];
        console.log(this.fossCategories);
      },
      (err) => {
        console.log('Failed to fetch foss categories');
        console.error(err);
      }
    );
  }

  ngOnInit() {
    // this.langData = { id: -1, name: "" };
    this.fetchAllFoss();
    // this.local_fossIndex = localStorage.getItem("fossIndex");
    // this.local_langId = localStorage.getItem("langId");

    // if (localStorage.length > 5) {
    //   this.getLanguage(this.local_fossIndex)
    //   this.fetchFossTutorials(this.local_langId)
    // }
  };

}
